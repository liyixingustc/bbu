

class mapper:
    def __init__(self, mapping, page, panel, widget, func):
        self.mapping = mapping
        self.page = str(page)
        self.panel = str(panel)
        self.widget = str(widget)
        self.func = str(func)

    def __call__(self, request, *args, **kwargs):
        register = self.mapping[
                                (self.mapping['page'] == self.page)&
                                (self.mapping['panel'] == self.panel)&
                                (self.mapping['widget'] == self.widget)&
                                (self.mapping['func'] == self.func)
                                ]['register'][0]

        response = register(request, *args, **kwargs)
        return response
