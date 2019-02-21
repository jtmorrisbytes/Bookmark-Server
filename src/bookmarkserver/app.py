from .database import db, ma, ShortUrl, short_url_schema
from flask import Flask, redirect, render_template, flash, url_for, request
from urllib.parse import quote, urlparse
from . import config
from webargs.flaskparser import use_args
from webargs import fields
import requests
import favicon


bookmark_server = Flask(__name__, template_folder='templates')
bookmark_server.config.from_object(config)
db.init_app(bookmark_server)
ma.init_app(bookmark_server)
with bookmark_server.app_context():
    db.create_all()

connection_timeout = bookmark_server.config.get('CONNECTION_TIMEOUT_LIMIT', 15)

def make_request(request_uri, timeout=connection_timeout):
    parsed_uri = urlparse(request_uri)
    if all([parsed_uri.scheme, parsed_uri.netloc]):
        print('checks pass')
        try:
            response = requests.get(request_uri, timeout=timeout)
        except requests.exceptions.ConnectionError:
            flash('Failed to verify the longuri "' +
                    request_uri + '" ' +
                'please check the url and your '+
                'internet connection and try again',
                category='danger')
        except requests.exceptions.ConnectTimeout:
            flash('The connection to "' + request_uri + '" '+
                'took longer than ' + timeout + ' seconds.' +
                'please try again later', category='info')
        except requests.exceptions.ReadTimeout:
            flash('The connection to "' + request_uri + '" timed out ' +
                'while waiting for the server to send data.' +
                ' Please try again later', category='info')
        else:
            if response.status_code == 404:
                flash('The webpage or resource at the url "' + request_uri +
                    'was not found', category='info')
            return response
    else:
        flash('The url "' + request_uri + '" is not valid',
        category='danger')
        return None
def get_data(request_uri, timeout=connection_timeout):
    response = make_request(request_uri,)
    if response.status_code !=200 or response.data is None:
        return None
    else:
        return response.data
def download_icon(request_uri, timeout=connection_timeout):
    icons =favicon.get(request_uri)
    if icons[0]:
        icon = get_data(icons[0].url, timeout=timeout)
        return icon
    else:
        return None
   
def get_icon_url(request_uri, timeout=connection_timeout):
    icons =favicon.get(request_uri)
    return icons[0].url





def sendError(errCode, short_error_message, long_error_message, redirectDelay=connection_timeout, redirectURL = '/'):
        
        return render_template('error.html',
                               errorCode=errCode,
                               short_error_message=short_error_message,
                               short_error_message_urlsafe=quote(short_error_message),
                               long_error_message=long_error_message,
                               redirect_delay=redirectDelay,
                               redirect_url=redirectURL
                               ),errCode
show_bookmarks_defaults= {
    'shortName':None,
    'longUri':None,
}
@bookmark_server.route('/bookmark/<string:shortName>', methods=['GET'])

def do_redirect(shortName):
    print("fetching link shortname: "+ shortName)
    if len(shortName) > 0:
        shortUrl = ShortUrl.query.filter_by(shortname=shortName).first()
        print("shorturl databse find: " + str(shortUrl))
        if shortUrl is not None:
            return redirect(shortUrl.longuri, 302)
        else:
                flash('I did not find the short name "' + shortName + '" in the database',
                category='info')
    return redirect('/',302)

        
@bookmark_server.route('/', methods=['GET'])
@use_args({'longuri':fields.String(required=False, default="https://www.google.com/"),
           'shortname': fields.String(required=False)})
def show_bookmarks(args):
    shorturls = ShortUrl.query.all()
    return render_template('form.html',
                            longUri=args.get('longuri'),
                            shortName=args.get('shortname'),
                            shorturls=shorturls,
                            numurlcolumns=4)

@bookmark_server.route('/', methods=['POST'])
@use_args(short_url_schema)
def add_bookmark(args):
    timeout = bookmark_server.config.get('CONNECTION_TIMEOUT_LIMIT')
    page = None
    icons = None
    print(args)
    if hasattr(args, 'longuri') and hasattr(args, 'shortname'):
        shorturl_match_list = ShortUrl.query.filter_by(shortname=args.shortname).all()
        if len(shorturl_match_list)> 0:
            flash("The shortname  '"  + args.shortname +"' already exists", category='danger')
            return redirect(url_for('show_bookmarks'), 302)
            
        response = make_request(args.longuri)
        if response is not None:
            icon = favicon.get(args.longuri)[0]
            if not icon:
                iconurl="https://via.placeholder/com/75x75"
            else:
                iconurl = icon.url
            # shortened_url = ShortUrl(shortname=args.shortname,
            #                          longuri=args.longuri,
            #                          iconurl=iconurl)
            args.iconurl = iconurl
            args.shortname = args.shortname.lower()

            db.session.add(args)
            db.session.commit()
            available_url = urlparse(request.url)
            available_url = available_url.scheme +"://" + available_url.netloc + '/bookmark/' + args.shortname
            flash("added your bookmark! its available at " + available_url, category='success')
            
           
    else:
        if not hasattr(args,'longuri'):
            flash('The parameter longUri is required', category='warning')
        if not hasattr(args, 'shortname'):
            flash('The parameter "shortname" is required', category='warning')

        
    
    return redirect(url_for('show_bookmarks'),302)
