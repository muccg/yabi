import mimetypes
import os

class MultipartFormEncoder(object):
    def __init__(self, chunksize=8192):
        self.chunksize = chunksize
        self.boundary = '----------ThIs_Is_tHe_bouNdaRY_$' 
        self.content_type = 'multipart/form-data; boundary=%s' % self.boundary
        self.eol = '\r\n'

    def encode(self, fields=None, files=None):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, path) elements for data to be uploaded as files
        Return FilelikeBody that returns data when read()
        """
        if fields is None: fields = tuple()
        if files is None: files = tuple()
        self.body = FilelikeBody()
        for field in fields:
            self.encode_field(field)
        for f in files:
            self.encode_file(f)
        self.end_form()

        return self.body

    def encode_field(self, field):
        name, value = field
        self.body.add_string('--' + self.boundary + self.eol)
        self.body.add_string('Content-Disposition: form-data; name="%s"' % name + self.eol)
        self.body.add_string(self.eol + value + self.eol)

    def encode_file(self, f): 
        name, filename, path = f
        self.body.add_string('--' + self.boundary + self.eol)
        self.body.add_string('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename) + self.eol)
        self.body.add_string('Content-Type: %s' % self.file_content_type(filename) + self.eol)
        self.body.add_string(self.eol)
        self.body.add_file(path)
        self.body.add_string(self.eol)

    def end_form(self):
        self.body.add_string('--' + self.boundary + '--' + self.eol)
        self.body.add_string(self.eol)

    def file_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
       

class FilelikeBody(object):
    def __init__(self):
        self.data = []
        self.open_files = {}
        self.reset()

    def add_string(self, item):
        self.data.append(item)

    def add_file(self, file_path):
        self.data.append(FilelikeBody.File(file_path))

    def seek(self, pos):
        if pos == 0:
            self.index = 0
        if 0 >= pos < len(self):
            self.index = pos

    def reset(self):
        self.seek(0)

    def read(self, size):
        item_idx, rel_pos = self.find_item_containing(self.index)
        if item_idx == -1:
            self.close()
            return ''
        result = str(self.read_from_item(item_idx, rel_pos, size))
        while len(result) < size and item_idx+1 < len(self.data):
            item_idx += 1
            rel_pos = 0
            result += str(self.read_from_item(item_idx, rel_pos, size))
        self.index += len(result)
        return result 

    def close(self):
        copy = self.open_files
        self.open_files = {}
        for f in copy.values():
            f.close()

    def __len__(self):
        return reduce(lambda s,item: s+len(item), self.data, 0)

    # Implementation

    class File(object):
        def __init__(self, path):
            self.path = path

        def __len__(self):
            return os.stat(self.path).st_size

    def find_item_containing(self, position):
        size = 0
        for i,l in enumerate([len(item) for item in self.data]):
            size += l
            if position < size:
                return i, position-(size-l)
        return -1, 0

    def open_file(self, name):
        return self.open_files.setdefault(name, open(name))

    def read_from_file(self, filename, start, size):
        f = self.open_file(filename)
        if f.tell() != start:
            f.seek(start)
        return f.read(size)

    def read_from_item(self, item_index, start, size):
        item = self.data[item_index]
        if hasattr(item, '__getslice__'):
            return item[start:start+size]
        else:
            return self.read_from_file(item.path, start, size)

 
