from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from bson.objectid import ObjectId
from app.common.subscriber.forms import SettingsForm
from app.common.subscriber.entry import Device
from app import app
import json


# routes
class SubscriberView(FlaskView):
    route_base = "/subscriber"

    @login_required
    def profile(self):
        return render_template('subscriber/profile.html')

    @login_required
    def channels(self):
        streams = []
        for serv in current_user.servers:
            streams += serv.streams
        return render_template('subscriber/channels.html', streams=streams, selected_streams=current_user.streams)

    @route('/apply_channels', methods=['POST'])
    @login_required
    def apply_channels(self):
        current_user.streams = []
        json_str = request.form['apply_channels_official_ids']
        if json_str:
            for sid in json.loads(json_str):
                current_user.streams.append(ObjectId(sid))
        current_user.save()
        return redirect(url_for('SubscriberView:channels'))

    @login_required
    def devices(self):
        return render_template('subscriber/devices.html')

    @login_required
    def downloads(self):
        return render_template('subscriber/downloads.html',
                               name=app.config['PUBLIC_CONFIG']['player']['name'],
                               name_lowercase=app.config['PUBLIC_CONFIG']['player']['name_lowercase'],
                               version=app.config['PUBLIC_CONFIG']['player']['version'])

    @route('/add_device', methods=['POST'])
    @login_required
    def add_device(self):
        device = Device(name=request.form['name'])
        current_user.add_device(device)
        return render_template('subscriber/devices.html')

    @route('/remove_device/<did>', methods=['POST'])
    @login_required
    def remove_device(self, did):
        current_user.remove_device(did)
        return render_template('subscriber/devices.html')

    @login_required
    def build_installer_request(self):
        return render_template('subscriber/profile.html')

    @route('/settings', methods=['POST', 'GET'])
    @login_required
    def settings(self):
        form = SettingsForm(obj=current_user.settings)

        if request.method == 'POST':
            if form.validate_on_submit():
                form.update_settings(current_user.settings)
                current_user.save()
                return render_template('subscriber/settings.html', form=form)

        return render_template('subscriber/settings.html', form=form)

    @login_required
    def logout(self):
        current_user.logout()
        return redirect(url_for('HomeView:index'))

    @login_required
    def remove(self):
        current_user.delete()
        return redirect(url_for('HomeView:index'))
