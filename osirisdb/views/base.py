# -*- coding: utf-8 -*-
"""
Base classes for making an API
"""

from flask.views import MethodView

class ViewBase(object):
    """A view base connects RESTful actions."""
    
    model = None
    
    def get_one(self, identifier):
        """Get all objects, or object by id."""
        return self.model.query.get_or_404(identifier)
    
    def get_many(self):
        """Get the full index."""
        return self.model.query.all()
        
    @classmethod
    def register_api(cls, app, endpoint, url, pk='identifier', pk_type='int'):
        view_func = cls.as_view(endpoint)
        app.add_url_rule(url, defaults={pk: None},
                         view_func=view_func, methods=['GET',])
        app.add_url_rule(url, view_func=view_func, methods=['POST',])
        app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                         methods=['GET', 'PUT', 'DELETE'])
