/*
YUI 3.5.1 (build 22)
Copyright 2012 Yahoo! Inc. All rights reserved.
Licensed under the BSD License.
http://yuilibrary.com/license/
*/
YUI.add("uploader-html5",function(d){var a=d.substitute,c=d.Uploader.Queue;function b(e){b.superclass.constructor.apply(this,arguments);}d.UploaderHTML5=d.extend(b,d.Widget,{_fileInputField:null,_buttonBinding:null,queue:null,initializer:function(){this._fileInputField=null;this.queue=null;this._buttonBinding=null;this.publish("fileselect");this.publish("uploadstart");this.publish("fileuploadstart");this.publish("uploadprogress");this.publish("totaluploadprogress");this.publish("uploadcomplete");this.publish("alluploadscomplete");this.publish("uploaderror");this.publish("dragenter");this.publish("dragover");this.publish("dragleave");this.publish("drop");},renderUI:function(){var g=this.get("boundingBox"),e=this.get("contentBox"),f=this.get("selectFilesButton");f.setStyles({width:"100%",height:"100%"});e.append(f);this._fileInputField=d.Node.create(b.HTML5FILEFIELD_TEMPLATE);e.append(this._fileInputField);},bindUI:function(){this._bindSelectButton();this._setMultipleFiles();this._bindDropArea();this._triggerEnabled();this.after("multipleFilesChange",this._setMultipleFiles,this);this.after("enabledChange",this._triggerEnabled,this);this.after("selectFilesButtonChange",this._bindSelectButton,this);this.after("dragAndDropAreaChange",this._bindDropArea,this);this.after("tabIndexChange",function(e){this.get("selectFilesButton").set("tabIndex",this.get("tabIndex"));},this);this._fileInputField.on("change",this._updateFileList,this);this.get("selectFilesButton").set("tabIndex",this.get("tabIndex"));},_bindDropArea:function(f){var e=f||{prevVal:null};if(e.prevVal!==null){e.prevVal.detach("drop",this._ddEventHandler);e.prevVal.detach("dragenter",this._ddEventHandler);e.prevVal.detach("dragover",this._ddEventHandler);e.prevVal.detach("dragleave",this._ddEventHandler);}var g=this.get("dragAndDropArea");if(g!==null){g.on("drop",this._ddEventHandler,this);g.on("dragenter",this._ddEventHandler,this);g.on("dragover",this._ddEventHandler,this);g.on("dragleave",this._ddEventHandler,this);}},_bindSelectButton:function(){this._buttonBinding=this.get("selectFilesButton").on("click",this.openFileSelectDialog,this);},_ddEventHandler:function(g){g.stopPropagation();g.preventDefault();switch(g.type){case"dragenter":this.fire("dragenter");break;case"dragover":this.fire("dragover");break;case"dragleave":this.fire("dragleave");break;case"drop":var f=g._event.dataTransfer.files,e=[];d.each(f,function(i){e.push(new d.FileHTML5(i));});this.fire("fileselect",{fileList:e});var h=this.get("fileList");this.set("fileList",this.get("appendNewFiles")?h.concat(e):e);break;}},_setButtonClass:function(e,f){if(f){this.get("selectFilesButton").addClass(this.get("buttonClassNames")[e]);}else{this.get("selectFilesButton").removeClass(this.get("buttonClassNames")[e]);}},_setMultipleFiles:function(){if(this.get("multipleFiles")===true){this._fileInputField.set("multiple","multiple");}else{this._fileInputField.set("multiple","");}},_triggerEnabled:function(){if(this.get("enabled")&&this._buttonBinding===null){this._bindSelectButton();this._setButtonClass("disabled",false);this.get("selectFilesButton").setAttribute("aria-disabled","false");}else{if(!this.get("enabled")&&this._buttonBinding){this._buttonBinding.detach();this._buttonBinding=null;this._setButtonClass("disabled",true);this.get("selectFilesButton").setAttribute("aria-disabled","true");}}},_updateFileList:function(g){var f=g.target.getDOMNode().files,e=[];d.each(f,function(i){e.push(new d.FileHTML5(i));});this.fire("fileselect",{fileList:e});var h=this.get("fileList");this.set("fileList",this.get("appendNewFiles")?h.concat(e):e);},_uploadEventHandler:function(e){switch(e.type){case"file:uploadstart":this.fire("fileuploadstart",e);break;case"file:uploadprogress":this.fire("uploadprogress",e);break;case"uploaderqueue:totaluploadprogress":this.fire("totaluploadprogress",e);break;case"file:uploadcomplete":this.fire("uploadcomplete",e);break;case"uploaderqueue:alluploadscomplete":this.queue=null;this.fire("alluploadscomplete",e);break;case"file:uploaderror":this.fire("uploaderror",e);break;case"uploaderqueue:uploaderror":this.fire("uploaderror",e);break;}},openFileSelectDialog:function(){var e=this._fileInputField.getDOMNode();if(e.click){e.click();}},upload:function(i,g,j){var h=g||this.get("uploadURL"),f=j||this.get("postVarsPerFile"),e=i.get("id");f=f.hasOwnProperty(e)?f[e]:f;if(i instanceof d.FileHTML5){i.on("uploadstart",this._uploadStartHandler,this);i.on("uploadprogress",this._uploadProgressHandler,this);i.on("uploadcomplete",this._uploadCompleteHandler,this);i.on("uploaderror",this._uploadErrorHandler,this);i.startUpload(h,f,this.get("fileFieldName"));}},uploadAll:function(e,f){this.uploadThese(this.get("fileList"),e,f);},uploadThese:function(i,f,h){if(!this.queue){var g=f||this.get("uploadURL"),e=h||this.get("postVarsPerFile");this.queue=new c({simUploads:this.get("simLimit"),errorAction:this.get("errorAction"),fileFieldName:this.get("fileFieldName"),fileList:i,uploadURL:g,perFileParameters:e});this.queue.on("uploadstart",this._uploadEventHandler,this);this.queue.on("uploadprogress",this._uploadEventHandler,this);this.queue.on("totaluploadprogress",this._uploadEventHandler,this);this.queue.on("uploadcomplete",this._uploadEventHandler,this);this.queue.on("alluploadscomplete",this._uploadEventHandler,this);this.queue.on("uploaderror",this._uploadEventHandler,this);this.queue.startUpload();this.fire("uploadstart");}}},{HTML5FILEFIELD_TEMPLATE:"<input type='file' style='visibility:hidden; width:0px; height: 0px;'>",SELECT_FILES_BUTTON:"<button type='button' class='yui3-button' role='button' aria-label='{selectButtonLabel}' tabindex='{tabIndex}'>{selectButtonLabel}</button>",TYPE:"html5",NAME:"uploader",ATTRS:{appendNewFiles:{value:true},buttonClassNames:{value:{hover:"yui3-button-hover",active:"yui3-button-active",disabled:"yui3-button-disabled",focus:"yui3-button-selected"}},dragAndDropArea:{value:null,setter:function(e){return d.one(e);}},enabled:{value:true},errorAction:{value:"continue",validator:function(f,e){return(f===c.CONTINUE||f===c.STOP||f===c.RESTART_ASAP||f===c.RESTART_AFTER);}},fileFieldName:{value:"Filedata"},fileList:{value:[]},multipleFiles:{value:false},postVarsPerFile:{value:{}},selectButtonLabel:{value:"Select Files"},selectFilesButton:{valueFn:function(){return d.Node.create(a(d.UploaderHTML5.SELECT_FILES_BUTTON,{selectButtonLabel:this.get("selectButtonLabel"),tabIndex:this.get("tabIndex")}));}},simLimit:{value:2,validator:function(f,e){return(f>=1&&f<=5);}},uploadURL:{value:""}}});d.UploaderHTML5.Queue=c;},"3.5.1",{requires:["widget","substitute","node-event-simulate","file-html5","uploader-queue"]});
