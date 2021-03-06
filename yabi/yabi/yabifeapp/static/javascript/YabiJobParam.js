/*
 * Yabi - a sophisticated online research environment for Grid, High Performance
 * and Cloud computing.
 * Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  */

/**
 * YabiJobParam
 * create a new yabi job param corresponding to a tool param
 */
function YabiJobParam(job, obj, allowsBatching, editable, preloadValue) {
  this.job = job;
  this.payload = obj;
  this.isSensitiveData = false;
  this.isInputFile = false;
  this.isOutputFile = false;
  this.allowsBatching = allowsBatching;
  this.valid = false;
  this.filterGroupHash = [];
  this.switchName = obj['switch'];
  this.defaultValue = obj.default_value;
  this.subscribedParams = []; // these params change when this param changes
  this.consumableFiles = []; // items that could be consumed
  // actual items consumed. unless allowsBatching = true then this
  // will only be one file
  this.consumedFiles = [];
  this.isMandatory = true;
  this.editable = editable;

  var tempEl, namePlaceholderEl;

  this.displayName = obj.displayName;
  if (! obj.hasOwnProperty('displayName')) {
    this.displayName = obj['switch'];
  }

  if (preloadValue !== null) {
    this.defaultValue = preloadValue;
  }

  this.value = this.defaultValue;

  this.containerEl = document.createElement('div');
  this.containerEl.className = 'jobParam';

  if (!(this.payload.mandatory || this.payload.common)) {
    this.containerEl.style.display = 'none';
  }
  this.isMandatory = this.payload.mandatory;

  if (this.payload.file_assignment == 'batch' ||
      this.payload.file_assignment == 'all') {
    this.isInputFile = true;
  }

  if (this.payload.output_file === true) {
    this.isOutputFile = true;
  }
  this.isSensitiveData = this.payload.sensitive_data;

  //default to input
  this.renderMode = 'input';

  //work out how to render inputfile input elements
  if (this.isInputFile) {
    if (this.job.acceptsInput === true) {
      this.renderMode = 'select';
    } else {
      this.renderMode = 'fileselector';
    }
  } else if (this.payload.switch_use__display_text == 'switchOnly') {
    this.renderMode = 'checkbox';
  }

  var index;

  //or if not editable, make it a div
  if (!this.editable) {
    this.renderMode = 'viewonly';
    this.labelEl = document.createElement('label');
    this.labelEl.appendChild(document.createTextNode(this.displayName));
    this.containerEl.appendChild(this.labelEl);

    this.valueEl = document.createElement('div');
    this.valueEl.className = 'value';
    this.containerEl.appendChild(this.valueEl);

    for (index in this.defaultValue) {
      if (!Y.Lang.isObject(this.defaultValue[index])) {
        this.valueEl.appendChild(document.createTextNode(
            this.isSensitiveData ? '***' : this.defaultValue[index]));
      } else {
        //rendering differently per file type
        if (this.defaultValue[index].type == 'job') {
          tempEl = document.createElement('span');
          tempEl.className = 'acceptedExtension';

          if (this.job.workflow.isJobIdLoaded(this.defaultValue[index].jobId)) {
            tempEl.appendChild(document.createTextNode(
                this.job.workflow.getDisplayNameForJobId(
                    this.defaultValue[index].jobId)));
          } else {
            //register tempEl to be updated with name when it is loaded
            this.job.workflow.getJobForId(
                this.defaultValue[index].jobId).registerNameDependency(tempEl);
          }

          this.valueEl.appendChild(tempEl);
        } else if (this.defaultValue[index].type == 'jobfile') {
          tempEl = document.createElement('span');
          tempEl.className = 'acceptedExtension';

          if (this.job.workflow.isJobIdLoaded(this.defaultValue[index].jobId)) {
            var displayName = this.job.workflow.getDisplayNameForJobId(
                this.defaultValue[index].jobId);
            tempEl.appendChild(document.createTextNode(
                displayName + '/' + this.defaultValue[index].filename));
          } else {
            //register a placeholder el to be updated with name when loaded
            namePlaceholderEl = document.createElement('span');
            tempEl.appendChild(namePlaceholderEl);
            tempEl.appendChild('/' + this.defaultValue[index].filename);

            var job = this.job.workflow.getJobForId(
                this.defaultValue[index].jobId);
            job.registerNameDependency(namePlaceholderEl);
          }

          this.valueEl.appendChild(tempEl);
        } else if (this.defaultValue[index].type == 'file') {
          tempEl = document.createElement('span');
          tempEl.className = 'acceptedExtension';
          tempEl.appendChild(document.createTextNode(
              this.defaultValue[index].filename));

          this.valueEl.appendChild(tempEl);
        } else {
          this.valueEl.appendChild(document.createTextNode('other file input'));
        }
      }
    }

    this.setHelpText();

    return;
  }

  var key;

  //some parameters accept multiple possibleValues
  //render as a select
  if (this.payload.possible_values) {
    this.renderMode = 'select';

    //possible sub-elements are 'values' or 'filterGroup'
    if (this.payload.possible_values.value) {
      //coerce single values into an array
      if (!Y.Lang.isArray(this.payload.possible_values.value)) {
        this.possibleValues = [this.payload.possible_values.value];
      }

      this.possibleValues = this.payload.possible_values.value;
    }

    if (this.payload.possible_values.filterGroup) {
      key = '';
      if (this.payload.possible_values.filteredBySwitch) {
        key = this.job.paramValue(
            this.payload.possible_values.filteredBySwitch);
      }

      if (!Y.Lang.isArray(this.payload.possible_values.filterGroup)) {
        var possibleValues = [this.payload.possible_values.filterGroup];
        this.payload.possible_values.filterGroup = possibleValues;
      }

      for (index in this.payload.possible_values.filterGroup) {
        var possibleValues = this.payload.possible_values.filterGroup[index];
        var fgkey = this.payload.possible_values.filterGroup[index].key;
        this.filterGroupHash[fgkey] = possibleValues;
      }

      //set default
      this.possibleValues = this.filterGroupHash[key].value;
      if (preloadValue === null) {
        this.defaultValue = this.filterGroupHash[key]['default'];
      }

      //subscribe
      if (this.payload.possible_values.filteredBySwitch &&
          this.job.getParam(this.payload.possible_values.filteredBySwitch)) {
        var possibleValues = this.payload.possible_values.filteredBySwitch;
        this.job.getParam(possibleValues).addSubscriber(this);
      }
    }
  }

  //___LABEL EL___
  this.labelEl = document.createElement('label');
  if (this.payload.mandatory === true) {
    //this.labelEl.appendChild(document.createTextNode("* "));
    this.labelEl.className = 'mandatoryParamLabel';
  }
  this.labelEl.appendChild(document.createTextNode(this.displayName));
  this.containerEl.appendChild(this.labelEl);

  //___INPUT EL___
  if (this.renderMode == 'select') {
    this.inputEl = this.renderSelect(true);
  } else if (this.renderMode == 'input') {
    this.inputEl = document.createElement('input');
    if (this.isSensitiveData) {
      this.inputEl.type = 'password';
    }
    this.inputEl.value = this.defaultValue;
    this.inputEl.style.width = '180px';
  } else if (this.renderMode == 'checkbox') {
    this.inputEl = document.createElement('input');
    this.inputEl.type = 'checkbox';
    this.inputEl.value = 'Yes';
    this.inputEl.checked = (this.defaultValue.toString().length > 0);
  } else if (this.renderMode == 'fileselector') {
    this.fileSelector = new YabiFileSelector(this, false);
    this.inputEl = this.fileSelector.containerEl;
  }
  this.containerEl.appendChild(this.inputEl);

  //accepted extensions
  var ael = this.payload.acceptedExtensionList;

  this.acceptedExtensionList = new YabiAcceptedExtensionList(ael);
  this.acceptedExtensionList.allowsBatching = this.allowsBatching;

  if (this.renderMode != 'fileselector') {
    //dont show accepted extensions for a file selector (looks funny)
    this.containerEl.appendChild(this.acceptedExtensionList.containerEl);
  }

  this.setHelpText();

  //attach key events for changes/keypresses
  Y.one(this.inputEl).on('blur', this.userValidate, this);
  Y.one(this.inputEl).on('keyup', this.userValidate, this);
  Y.one(this.inputEl).on('change', this.userValidate, this);

  //run an initial validation on the default value
  this.validate();

  if (this.isInputFile && this.job.acceptsInput &&
      Y.Lang.isArray(this.defaultValue)) {
    this.consumableFiles = _.map(this.defaultValue, function(val) {
      return this.job.workflow.getJobForId(val.jobId);
    }, this);
    this.consumedFiles = _.clone(this.consumableFiles);
  }
}


/**
 * destroy
 *
 * purges event handlers, deletes dom related things that need to be cleared out
 */
YabiJobParam.prototype.destroy = function() {
  if (!Y.Lang.isUndefined(this.inputEl)) {
    Y.one(this.inputEl).detachAll();
  }
};


/**
 * hasChanged
 *
 * identifies if this value has changed from the default or preloaded value
 */
YabiJobParam.prototype.hasChanged = function() {
  //default value is stored in the payload
  if (this.defaultValue != this.getValue()) {
    return true;
  }
  return false;
};


/**
 * setHelpText
 *
 * Sets the help text for the given parameter.
 */
YabiJobParam.prototype.setHelpText = function(text) {
  text = text || this.payload.helptext;

  if (text) {
    if (!this.helpTextEl) {
      this.helpTextEl = document.createElement('div');
      this.helpTextEl.className = 'help';
      this.containerEl.appendChild(this.helpTextEl);
    }

    this.helpTextEl.innerHTML = text;
  }
};


/**
 * toggleDisplay
 *
 * hides or shows this parameter from view
 */
YabiJobParam.prototype.toggleDisplay = function(shouldDisplay) {
  //mandatory and common params are always shown
  if (this.payload.mandatory || this.payload.common) {
    return;
  }

  if (shouldDisplay) {
    this.containerEl.style.display = 'block';
  } else {
    this.containerEl.style.display = 'none';
  }
};


/**
 * emittedFiles
 *
 * if this parameter represents an inputFile or outputFile, then
 * emit a file array
 */
YabiJobParam.prototype.emittedFiles = function() {
  var value = this.getValue();

  if (value === '') {
     return [];
  }
  if (!(this.isInputFile || this.isOutputFile)) {
     return [];
  }

  if (!Y.Lang.isArray(value)) {
      value = [value];
  }

  return _.map(value, function(v) {
     return Y.Lang.isString(v) ? new YabiJobFileValue(this.job, v) : v;
  }, this);
};


/**
 * updatePossibleValues
 *
 * update the select drop-down with values, based on the
 * possibleValues json element
 */
YabiJobParam.prototype.updatePossibleValues = function(key) {
  //set default
  this.possibleValues = this.filterGroupHash[key].value;
  this.defaultValue = this.filterGroupHash[key]['default'];

  var inEl = this.renderSelect(true);
  this.containerEl.replaceChild(inEl, this.inputEl);
  this.inputEl = inEl;

  this.validate();
};


/**
 * optionallyConsumeFiles
 *
 * given an array of files, filter them down to a set of files that
 * are acceptable and render them in a drop-down if the current value
 * hasChanged from the default, then try to retain that selection
 * if not, choose the last valid option automatically as a pre-fill
 */
YabiJobParam.prototype.optionallyConsumeFiles = function(fileArray) {
  var updatedConsumable, updatedConsumed, a, b, index, counter, opt;

  // we can only consume files if we are an input param
  //  for a job that accepts inputs
  if (this.isInputFile && this.job.acceptsInput) {
    // first pass, validate that currently consumable/consumed items
    // are still valid
    updatedConsumable = [];
    updatedConsumed = [];
    for (index in this.consumableFiles) {
      for (var subindex in fileArray) {
        a = this.consumableFiles[index];
        b = fileArray[subindex];
        if (a.isEqual(b)) {
          updatedConsumable.push(a); //retain this item

          //check if it is currently consumed
          for (var consumeIndex in this.consumedFiles) {
            if (this.consumedFiles[consumeIndex].isEqual(b)) {
              updatedConsumed.push(a);
              break;
            }
          }

          break;
        }
      }
    }
    // this is the new list of items already consumable
    this.consumableFiles = updatedConsumable.slice();
    // new list of valid consumed files
    this.consumedFiles = updatedConsumed.slice();

    // second pass, if we have no inputs now (old consumable items are all
    // invalid or didn't exist), add new ones
    this.consumableFiles = [];
    for (index in fileArray) {
      if (this.acceptedExtensionList.validForValue(fileArray[index])) {
        this.consumableFiles.push(fileArray[index]);
      }
    }

    //render consumable files
    if (this.renderMode == 'select') {
      //purge existing options
      while (this.inputEl.firstChild) {
        this.inputEl.removeChild(this.inputEl.firstChild);
      }

      //if non-mandatory, insert a blank value
      if (this.payload.mandatory !== true) {
        opt = document.createElement('option');
        opt.setAttribute('value', '');

        if (this.consumedFiles.length === 0) {
          opt.setAttribute('selected', 'true');
        }

        this.inputEl.appendChild(opt);
      }

      counter = 1;
      for (index in this.consumableFiles) {
        opt = document.createElement('option');
        opt.setAttribute('value', '' + this.consumableFiles[index]);

        //since we only allow one selection, check for that item
        if (this.consumedFiles.length > 0 &&
            this.consumedFiles[0].isEqual(this.consumableFiles[index])) {
          opt.setAttribute('selected', 'true');
        }

        if (this.payload.mandatory === true) {
          if (this.consumedFiles.length === 0 &&
              this.consumableFiles.length == counter++) {
            opt.setAttribute('selected', 'true');
          }
        }

        opt.appendChild(document.createTextNode(
            '' + this.consumableFiles[index]));
        this.inputEl.appendChild(opt);
      }
    }

    //update value of consumedFiles if it is no longer valid
    if (this.consumedFiles.length === 0) {
      if (this.payload.mandatory === true) {
        //default to just selecting the last valid option
        this.consumedFiles = this.consumableFiles.slice(
            this.consumableFiles.length - 1, 1);
      }
    }

    //render consumed files
    if (this.renderMode == 'input') {
      this.inputEl.value = this.consumedFiles.toString();
    }

    //finally, validate
    this.validate();
  }
};


/**
 * getValue
 *
 * returns an array or single value that represents the string, file
 * or other input
 */
YabiJobParam.prototype.getValue = function(useInternal) {
  if (useInternal === null) {
    useInternal = false;
  }

  if (!this.editable) {
    return this.defaultValue;
  }

  if (this.renderMode == 'input') {
    if (this.inputEl.value === '') {
      return '';
    }

    if (this.isInputFile) {
      return new YabiJobFileValue(this.job, this.inputEl.value);
    }

    return this.inputEl.value;
  } else if (this.renderMode == 'checkbox') {
    if (this.inputEl.checked) {
      return 'Yes';
    }

    return '';
  } else if (this.renderMode == 'select') {

    if (this.inputEl.options.length === 0 || this.inputEl.selectedIndex < 0) {
      return '';
    }

    if (this.isInputFile) {
      return this.consumedFiles.slice();
    }

    return this.inputEl.options[this.inputEl.selectedIndex].value;

  } else if (this.renderMode == 'fileselector') {
    return this.fileSelector.getValues(useInternal);
  }
};


/**
 * focus
 *
 * focusses the input, if possible
 */
YabiJobParam.prototype.focus = function() {
  if (!this.editable) {
    return;
  }

  if (this.renderMode == 'input' || this.renderMode == 'checkbox') {
    this.inputEl.focus();
  }
};


/**
 * toJSON
 *
 * interestingly, returns internal values, not emitted values
 * ie file paths are YabiSimpleFileValues, not YabiJobFileValues
 */
YabiJobParam.prototype.toJSON = function() {
  var value = this.getValue(true);

  if (!value && !this.isMandatory) {
    return null;
  }

  if (!Y.Lang.isArray(value)) {
    value = [value];
  }

  var munge = function(val) {
    if (val instanceof YabiSimpleFileValue) {
      return val;
    } else if (val instanceof YabiJob) {
      return { 'type': 'job',
               'jobId': val.jobId };
    } else if (val instanceof YabiJobFileValue) {
      return { 'type': 'jobfile',
               'jobId': val.job.jobId,
               'filename': val.filename };
    } else {
      return val;
    }
  };

  var result = { 'switchName': this.switchName,
    'valid': this.valid,
    'value': _.map(value, munge)
 };

  return result;
};


/**
 * addSubscriber
 *
 * subscribes one parameter to be notified of changes in value of this parameter
 */
YabiJobParam.prototype.addSubscriber = function(subscriber) {
  this.subscribedParams.push(subscriber);
};


/**
 * validate
 *
 * validate current value
 */
YabiJobParam.prototype.validate = function() {

  //sync this.consumedFiles to the value of the input
  if (this.renderMode == 'input') {
    this.consumedFiles = [this.getValue()];
  } else if (this.renderMode == 'select') {
    if (this.isInputFile) {
      if (this.payload.mandatory === true) {
        this.consumedFiles = this.consumableFiles.slice(
            this.inputEl.selectedIndex, this.inputEl.selectedIndex + 1);
      } else {
        // non-mandatory values have a blank entry, so we need to
        // account for that
        if (this.inputEl.selectedIndex === 0) {
          this.consumedFiles = '';
        } else {
          this.consumedFiles = this.consumableFiles.slice(
              this.inputEl.selectedIndex - 1, this.inputEl.selectedIndex);
        }
      }

    } else {
      //dealing with possible values

    }
  } else if (this.renderMode == 'fileselector') {
    this.consumedFiles = this.getValue();
  }

  this.valid = true;

  //check for empty mandatory
  if (this.payload.mandatory === true && this.getValue().length === 0) {
    //console.log("failed mandatory test");
    this.valid = false;
  }

  //if this is meant to be an input file, validate filetypes
  if (this.isInputFile) {
    // first, verify that consumedFiles exist, if so then we are fine

    if (this.consumedFiles.length === 0) {

      // alternatively, check if the user has manually typed some text that
      // hasn't become a 'consumed file'
      if (!this.acceptedExtensionList.validForValue(this.getValue())) {

        //console.log("failed the valid extension test");
        this.valid = false;
      }
    }
  }

  //render internal validation
  if (!this.valid) {
    if (this.renderMode == 'fileselector') {
      this.fileSelector.renderInvalid();
    } else {
      this.inputEl.className = 'invalidParam';
    }
  } else {
    if (this.renderMode == 'fileselector') {
      this.fileSelector.renderValid();
    } else {
      this.inputEl.className = 'validParam';
    }
  }

};


/**
 * renderSelect
 *
 * renders the select element (if there is one)
 */
YabiJobParam.prototype.renderSelect = function(allowDefault) {
  var selectEl = document.createElement('select');
  selectEl.style.width = '180px';
  var option;

  //render possibleValues
  if (!this.isInputFile && this.possibleValues) {
    for (var index in this.possibleValues) {
      option = document.createElement('option');
      option.setAttribute('value', this.possibleValues[index].value);

      if (this.possibleValues[index].type &&
          this.possibleValues[index].type == 'group') {
        option.setAttribute('disabled', 'true');
        option.appendChild(document.createTextNode(
            this.possibleValues[index].display));
      } else {
        option.appendChild(document.createTextNode('   '));
        option.appendChild(document.createTextNode(
            this.possibleValues[index].display));
      }

      if (allowDefault &&
          this.possibleValues[index].value == this.defaultValue) {
        option.setAttribute('selected', 'true');
      }

      selectEl.appendChild(option);
    }
  }

  return selectEl;
};

// --------- callback methods, these require a target via their inputs --------


/**
 * userValidate
 *
 * fires on user intervention
 */
YabiJobParam.prototype.userValidate = function(e) {
  this.validate();

  //propagate to subscribed params
  for (var index in this.subscribedParams) {
    this.subscribedParams[index].updatePossibleValues(this.getValue());
  }

  //notify job of validation, propagating the validation from top to bottom
  this.job.checkValid(true);
};
