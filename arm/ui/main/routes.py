"""
Automatic Ripping Machine - User Interface (UI) - Blueprint
    Main

Covers
    - index [GET]
"""
import flask
from flask import render_template, redirect, session
from flask_login import LoginManager, login_required, \
    current_user, login_user, logout_user
from flask import current_app as app

from arm.models.job import Job
from arm.models.system_info import SystemInfo
from arm.models.ui_settings import UISettings
from arm.models.user import User
import arm.config.config as cfg
import arm.ui.settings.ServerUtil
from arm.ui.settings.routes import check_hw_transcode_support


# This attaches the armui_cfg globally to let the users use any bootswatch skin from cdn
# remove this once all blueprints finalised
# try:
#     armui_cfg = ui_utils.arm_db_cfg()
# except Exception as error:
#     ui_utils.setup_database()


@app.route('/')
@app.route('/index.html')
@app.route('/index')
@login_required
def home():
    """
    The main homepage showing current rips and server stats
    """

    # Set UI Config values for cookies
    # the database should be available and data loaded by this point
    try:
        armui_cfg = UISettings.query.filter_by().first()
    except Exception as error:
        return render_template('error.html', error=error)

    # Push out HW transcode status for homepage
    stats = {'hw_support': check_hw_transcode_support()}

    # System details in class server
    server = SystemInfo.query.filter_by(id="1").first()
    serverutil = arm.ui.settings.ServerUtil.ServerUtil()

    # System details in class server
    arm_path = cfg.arm_config['TRANSCODE_PATH']
    media_path = cfg.arm_config['COMPLETED_PATH']

    # Page titles
    session["arm_name"] = cfg.arm_config['ARM_NAME']
    session["page_title"] = "Home"

    # if os.path.isfile(cfg.arm_config['DBFILE']):
    #     jobs = {}
    #     # try:
    #     #     jobs = db.session.query(Job).filter(Job.status.notin_(['fail', 'success'])).all()
    #     # except Exception:
    #     #     # db isn't setup
    #     #     return redirect(url_for('setup'))
    # else:
    jobs = {}

    response = flask.make_response(render_template("index.html",
                                                   jobs=jobs,
                                                   children=cfg.arm_config['ARM_CHILDREN'],
                                                   server=server,
                                                   serverutil=serverutil,
                                                   arm_path=arm_path,
                                                   media_path=media_path,
                                                   stats=stats))
    # remove the unused cookies if not required by other functions/pages
    # response.set_cookie("use_icons", value=f"{armui_cfg.use_icons}")
    # response.set_cookie("save_remote_images", value=f"{armui_cfg.save_remote_images}")
    # response.set_cookie("bootstrap_skin", value=f"{armui_cfg.bootstrap_skin}")
    # response.set_cookie("language", value=f"{armui_cfg.language}")
    response.set_cookie("index_refresh", value=f"{armui_cfg.index_refresh}")
    # response.set_cookie("database_limit", value=f"{armui_cfg.database_limit}")
    # response.set_cookie("notify_refresh", value=f"{armui_cfg.notify_refresh}")
    return response


@app.login_manager.user_loader
def load_user(user_id):
    """
    Logged in check
    :param user_id:
    :return:
    """
    try:
        return User.query.get(int(user_id))
    except Exception:
        app.logger.debug("Error getting user")
        return None


@app.login_manager.unauthorized_handler
def unauthorized():
    """
    User isn't authorised to view the page

    :return:
        Page redirect
    """
    return redirect('/login')
