# -*- coding: utf-8 -*-
from flask import render_template
from flask.views import View

import os
import datetime
from os.path import join as pjoin


class ArchiveView(View):
    """A view of an archive."""
    
    def __init__(self, model, template, datefield='date', modelcontextname=None, perpage=100):
        super(ArchiveView, self).__init__()
        self.model = model
        self.template = template
        self._datefield = datefield
        self.modelcontextname = modelcontextname or (self.model.__name__.lower() + "s")
        self.perpage = perpage
    
    def dispatch_request(self, year=None, month=None, day=None, page=None):
        """Archive request dispatcher."""
        start = datetime.date(year, month or 1, day or 1)
        if month is None:
            end = datetime.date(year + 1, 1, 1)
        elif day is None:
            _year = year + (month // 12)
            _month = ((month + 1) % 12) + 1
            end = datetime.date(_year, _month, 1)
        else:
            end = start + datetime.timedelta(days=1)
        objects = self.model.query.filter(getattr(self.model,self._datefield).between(start, end)).paginate(page, per_page=self.perpage)
        context = {self.modelcontextname:objects, 'year':year, 'month':month, 'day':day}
        return render_template(pjoin(self.template, 'archive.html'), **context)
    
    @classmethod
    def register(cls, api, endpoint, model, template, prefix='archive', **kwargs):
        """Register this object as an endpoint"""
        view_func = cls.as_view(endpoint, model, template, **kwargs)
        base = ''
        for part in ['<int:year>','<int:month>','<int:day>']:
            base = pjoin(base, part)
            api.add_url_rule(pjoin(prefix, base) + '/', view_func=view_func, methods=['GET'])
            api.add_url_rule(pjoin(prefix, base, 'page', '<int:page>') + '/', view_func=view_func, methods=['GET'])
        
        