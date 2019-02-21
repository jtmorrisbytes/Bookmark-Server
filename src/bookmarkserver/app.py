from .database import db, ma, ShortUrl, short_url_schema
from flask import Flask, redirect, render_template, flash, url_for
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
        flash("The url " + request_uri + 'is not valid',
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
@bookmark_server.route('/<string:shortName>', methods=['GET'])

def do_redirect(shortName):
        if len(shortName) > 0:
            shortUrl = ShortUrl.query.filter_by(shortname=shortName)
            if shortUrl is not None:
                if hasattr(shortUrl, 'url'):
                    return redirect(shortUrl.url)
                else:
                    return sendError(errCode=501,
                                        short_error_message='Url not found for shortname "' + shortName + '"',
                                        long_error_message =  'I could not find the related URL for ' + shortName + 'in the database,'
                                        )
            else:
                    return sendError(
                    'error.html',
                    errorCode=404,
                    short_error_message='shortname not found',
                    long_error_message=
                    'I did not find the shortname "' + shortName +
                    '" in the database'
            )
        else:
            return redirect('/',300)

        
@bookmark_server.route('/', methods=['GET'])
@use_args({'longuri':fields.String(required=False),
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
            db.session.add(args)
            db.session.commit()
            
           
    else:
        if not hasattr(args,'longuri'):
            flash('The parameter longUri is required', category='warning')
        if not hasattr(args, 'shortname'):
            flash('The parameter "shortname" is required', category='warning')

        
    
    return redirect(url_for('show_bookmarks'),302)
