# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template, redirect, g

from ..core import api
from ..models import SpecFrame
from ...views.base import ViewBase
from ...views.targets import select_target_form
from ...model.target import Target
from ...application import db

__all__ = ['SpecFrameView']

class SpecFrameBase(ViewBase):
    """
    SpecFrame API base
    """
    model = SpecFrame
    

class SpecFrameView(SpecFrameBase, MethodView):
    """Method view to render the dataset."""
    
    def get(self, identifier=None):
        """Get the dataset view."""
        if identifier is None:
            return render_template("frames/list.html", frames=self.get_many())
        return render_template("frames/item.html", frame=self.get_one(identifier))
        

SpecFrameView.register_api(api, 'specframe', 'frames/')

@api.route("frames/<int:id>/target/", methods=('POST',))
def set_frame_target(id):
    """Set the target for a particular frame."""
    form = select_target_form    
    if form.validate_on_submit():
        frame = SpecFrame.query.get(id)
        if form.target.data == -1:
            frame.target = None
        else:
            target = Target.query.get(form.target.data)
            frame.target = target
        db.session.add(frame)
        db.session.commit()
        return redirect(form.prev.data)
    return redirect(form.prev.data)