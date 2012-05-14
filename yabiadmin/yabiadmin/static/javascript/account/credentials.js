var YabiAccountCredentials = function(account) {
  var self = this;

  this.account = account;
  this.credentials = [];
  this.item = this.account.list.createItem('credentials');
  this.list = null;

  this.item.addEventListener('deselect', function() {
    self.account.destroyRightColumn();
    self.destroyList();
  });

  this.item.addEventListener('select', function() {
    self.createList();
    self.account.destroyRightColumn();
  });
};

YabiAccountCredentials.prototype.createList = function(id) {
  var self = this;
  var connection = null;
  var container = document.querySelector('.yabiMiddleColumn');

  this.destroyList();

  var loading = new YAHOO.ccgyabi.widget.Loading(container);
  loading.show();

  this.list = new RadioList(container);
  this.list.list.className += ' credentials';

  Y.use('*', function(Y) {
    var callback = {
      success: function(trans_id, o) {
        var credentials;

        credentials = Y.JSON.parse(o.responseText);

        for (var i = 0; i < credentials.length; i++) {
          var credential = new YabiCredential(self, credentials[i]);
          self.credentials.push(credential);

          if (id && credentials[i].id == id) {
            self.list.selectItem(credential.item);
          }
        }

        loading.hide();
      },
      failure: function(trans_id, o) {
        YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
        loading.hide();
      }
    };

    Y.on('io:success', callback.success, Y);
    Y.on('io:failure', callback.failure, Y);

    Y.io(appURL + 'ws/account/credential');
  });
  

};

YabiAccountCredentials.prototype.destroyList = function() {
  if (this.list) {
    this.list.destroy();
    this.list = null;
  }
};


var YabiCredential = function(credentials, credential) {
  var self = this;

  this.credential = credential;
  this.credentials = credentials;
  this.container = null;
  this.item = credentials.list.createItem(this.createLabel());
  this.template = document.getElementById('credential');

  this.item.addEventListener('deselect', function() {
    if (self.container) {
      document.querySelector('.yabiRightColumn').removeChild(self.container);
      self.container = null;
      self.form = null;
    }
  });

  this.item.addEventListener('select', function() {
    if (self.container) {
      document.querySelector('.yabiRightColumn').removeChild(self.container);
    }

    self.createForm();
  });
};

YabiCredential.prototype.createForm = function() {
  var self = this;

  this.container = this.template.cloneNode(true);
  this.container.className = null;
  this.container.id = null;
  this.form = this.container.querySelector('form');

  var isOnRecord = function(value, container, setPlaceholder, 
                            unsetPlaceholder) {
    var record = container.querySelector('.record');
    var input = container.querySelector('input, textarea');
    var recordDisplay = 'none';

    input.className = 'placeholder';
    input.value = value ? setPlaceholder : unsetPlaceholder;

    Y.use('*', function(Y) {
      var inputNode = Y.one(input);
      inputNode.on('focus', function(e) {
        input.className = '';
        input.value = '';
      });
    });

    if (value) {
      recordDisplay = 'block';
    }

    if (record) {
      record.style.display = recordDisplay;
    }
  };

  var username = this.credential.username;
  this.form.querySelector('.username-container input').value = username;

  isOnRecord(
      this.credential.password,
      this.form.querySelector('.password-container'),
      'placeholder',
      ''
  );

  // Hide the confirm password box until the password is actually changed.
  var confirmPasswordContainer = this.form.querySelector(
                                     '.confirm-password-container');
  var confirmPasswordInput = this.form.querySelector(
                                     '.password-container input');
  confirmPasswordContainer.style.display = 'none';

  var showConfirmPassword = function(e) {
    /* Animate displaying the confirm password box so the form doesn't jump
         * unexpectedly. */
    confirmPasswordContainer.style.overflow = 'hidden';
    confirmPasswordContainer.style.height = 0;
    confirmPasswordContainer.style.marginBottom = 0;
    confirmPasswordContainer.style.display = 'block';
    
    Y.use('*', function(Y) {
      var anim = new Y.Anim({
        node: Y.one(confirmPasswordContainer),
        to: {
          height: 20,
          marginBottom: 9
        },
        easing: 'easeOut',
        duration: 0.4

      }); 

      anim.run();
    });
  };

  Y.use('*', function(Y) {
    var node = Y.one(confirmPasswordInput);
    node.once('focus', showConfirmPassword);
  });

  isOnRecord(
      this.credential.certificate,
      this.form.querySelector('.certificate-container'),
      'To replace the certificate, paste the new certificate here.',
      ''
  );

  isOnRecord(
      this.credential.key,
      this.form.querySelector('.key-container'),
      'To replace the key, paste the new key here.',
      ''
  );

  var expiry = this.form.querySelector("select[name='expiry']");
  if (this.credential.expires_in) {
    var option = document.createElement('option');
    option.value = 'no';
    option.appendChild(document.createTextNode('current setting'));

    expiry.insertBefore(option, expiry.options.item(1));
    option.selected = true;
  }

  document.querySelector('.yabiRightColumn').appendChild(this.container);

  var form = this.form;
  Y.use('*', function(Y) {
    var formNode = Y.one(form);
    formNode.on('submit', function(e) {
      e.halt(true);
      self.save()
    });
  });
};

YabiCredential.prototype.createLabel = function() {
  var label = document.createElement('div');

  if (this.credential.backends.length > 0) {
    this.credential.backends.sort();
    for (var i = 0; i < this.credential.backends.length; i++) {
      /* Add zero-width spaces to ensure line wrapping occurs where
             * appropriate. */
      var name = this.credential.backends[i].replace(/\//g, '/\u200b');

      var div = document.createElement('div');
      div.className = 'label';
      div.appendChild(document.createTextNode(name));

      label.appendChild(div);
    }
  }
  else {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(this.credential.description));

    label.appendChild(div);
  }

  var div = document.createElement('div');
  div.className = 'expiry';
  div.appendChild(document.createTextNode(this.getExpiry()));

  label.appendChild(div);

  // Create the encryption badge.
  var badge = document.createElement('div');
  if (this.credential.encrypted) {
    badge.className = 'badgelocked';
    badge.title = 'encrypted credential';
  }
  else {
    badge.className = 'badgeunlocked';
    badge.title = 'unencrypted credential';
  }
  label.appendChild(badge);

  return label;
};

YabiCredential.prototype.getExpiry = function() {
  if (this.credential.expires_in !== null) {
    if (this.credential.expires_in < 0) {
      return 'expired';
    }

    try {
      return 'expires ' + YAHOO.ccgyabi.widget.EnglishTime(
                                           this.credential.expires_in);
    }
    catch (e) {
      return 'expires in an indeterminate length of time';
    }
  }
  else {
    return 'never expires';
  }
};

YabiCredential.prototype.save = function() {
  var self = this;
  var data = this.validate();

  if (data) {
    var callback = {
      success: function(transId, o) {
        YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);

        document.querySelector('.yabiRightColumn').removeChild(self.container);
        self.credentials.createList(self.credential.id);
      },
      failure: function(transId, o) {
        YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
        self.enableForm();
      }
    };

    var cfg = {
      method: 'POST',
      data: data
    };
    Y.once('io:success', callback.success, Y);
    Y.once('io:failure', callback.failure, Y);

    var request = Y.io(appURL + 'ws/account/credential/' + this.credential.id, cfg);

    self.disableForm();
  }
};

YabiCredential.prototype.validate = function() {
  var self = this;

  var data = {};
  var update = 0;

  var checkDelete = function(value, prompt) {
    if (value === '') {
      return window.confirm(prompt);
    }

    return true;
  };

  var getValue = function(name) {
    var element = self.form.querySelector("input[name='" + name + "'], " +
            "select[name='" + name + "'], textarea[name='" + name + "']");

    if (element && element.className.indexOf('placeholder') == -1) {
      return element.value;
    }

    return null;
  };

  var username = getValue('username');
  if (username !== null && username !== this.credential.username) {
    var areYouSureMsg = 'You have chosen to delete your username. ' +
                        'Are you sure you want to continue?';
    if (!checkDelete(username, areYouSureMsg)) {
      return null;
    }

    data.username = username;
    update++;
  }

  var password = getValue('password');
  if (password !== null) {
    if (password != getValue('confirm-password')) {
      YAHOO.ccgyabi.widget.YabiMessage.fail('Passwords do not match');
      return null;
    }

    var areYouSureMsg = 'You have chosen to delete your password. ' +
                        'Are you sure you want to continue?';
    if (!checkDelete(password, areYouSureMsg)) {
      return null;
    }

    data.password = password;
    update++;
  }

  var certificate = getValue('certificate');
  if (certificate !== null) {
    var areYouSureMsg = 'You have chosen to delete your certificate. ' +
                        'Are you sure you want to continue?';
    if (!checkDelete(certificate, areYouSureMsg)) {
      return null;
    }

    data.certificate = certificate;
    update++;
  }

  var key = getValue('key');
  if (key !== null) {
    var areYouSureMsg = 'You have chosen to delete your key. ' +
                        'Are you sure you want to continue?';
    if (!checkDelete(key, areYouSureMsg)) {
      return null;
    }

    data.key = key;
    update++;
  }

  var expiry = getValue('expiry');
  if (expiry != 'no') {
    data.expiry = expiry;
    update++;
  }

  if (update == 0) {
    YAHOO.ccgyabi.widget.YabiMessage.warn('Nothing to update');
    return null;
  }

  var encode = function(key, value) {
    var encodeComponent = function(s) {
      return encodeURIComponent(s).replace(' ', '%20');
    };

    return encodeComponent(key) + '=' + encodeComponent(value);
  };
  var formData = [];
  for (var key in data) {
    if (data.hasOwnProperty(key)) {
      formData.push(encode(key, data[key]));
    }
  }

  return formData.join('&');
};

YabiCredential.prototype.disableForm = function() {
  var elements = this.form.querySelectorAll('input, select, textarea');

  for (var i = 0; i < elements.length; i++) {
    elements[i].enabled = false;
  }
};

YabiCredential.prototype.enableForm = function() {
  var elements = this.form.querySelectorAll('input, select, textarea');

  for (var i = 0; i < elements.length; i++) {
    elements[i].enabled = true;
  }
};
