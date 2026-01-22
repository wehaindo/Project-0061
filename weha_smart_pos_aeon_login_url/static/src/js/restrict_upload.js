odoo.define('weha_smart_pos_aeon_login_url.restrict_upload', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    
    // Configuration - Edit these values as needed
    var ALLOWED_EXTENSIONS = [
        '.pdf', 
        '.jpg', '.jpeg', '.png', '.gif',
        '.doc', '.docx', '.xls', '.xlsx', '.csv',
        '.ppt', '.pptx', '.txt', '.zip', '.rar'
    ];
    
    var MAX_FILE_SIZE_MB = 10;
    var BYTES_PER_MB = 1024 * 1024;
    
    // Utility functions
    function getFileExtension(filename) {
        return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2).toLowerCase();
    }
    
    function validateFile(file) {
        var errors = [];
        var extension = '.' + getFileExtension(file.name);
        
        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            errors.push(_.str.sprintf(
                _t("File type '%s' is not allowed. Allowed types: %s"), 
                extension,
                ALLOWED_EXTENSIONS.join(', ')
            ));
        }
        
        if (file.size > MAX_FILE_SIZE_MB * BYTES_PER_MB) {
            errors.push(_.str.sprintf(
                _t("File size (%.2fMB) exceeds maximum allowed size (%sMB)."),
                file.size / BYTES_PER_MB,
                MAX_FILE_SIZE_MB
            ));
        }
        
        return errors.length ? errors.join(' ') : null;
    }
    
    // Patch FileUploader for general uploads (Odoo 16)
    var FileUploader = require('web.file_upload_mixin').FileUploader;
    FileUploader.include({
        _onUpload: function (ev) {
            var file = ev.target.files && ev.target.files[0];
            if (file) {
                var error = validateFile(file);
                if (error) {
                    this.do_warn(_t("Upload rejected"), error);
                    ev.target.value = '';
                    return false;
                }
            }
            return this._super.apply(this, arguments);
        },
    });
    
    // Patch FieldBinaryFile for form binary fields
    var FieldBinaryFile = require('web.basic_fields').FieldBinaryFile;
    FieldBinaryFile.include({
        _onFileChange: function (ev) {
            var file = ev.target.files && ev.target.files[0];
            if (file) {
                var error = validateFile(file);
                if (error) {
                    this.displayNotification({
                        title: _t("Upload rejected"),
                        message: error,
                        type: 'danger',
                    });
                    ev.target.value = '';
                    return;
                }
            }
            return this._super.apply(this, arguments);
        },
    });
    
    // For attachment uploads in Odoo 16
    var Chatter = require('mail.Chatter');
    if (Chatter) {
        Chatter.include({
            _onFileUploaded: function (ev) {
                var file = ev.target.files && ev.target.files[0];
                if (file) {
                    var error = validateFile(file);
                    if (error) {
                        this.displayNotification({
                            title: _t("Upload rejected"),
                            message: error,
                            type: 'danger',
                        });
                        ev.target.value = '';
                        return;
                    }
                }
                return this._super.apply(this, arguments);
            },
        });
    }
    
    return {
        ALLOWED_EXTENSIONS: ALLOWED_EXTENSIONS,
        MAX_FILE_SIZE_MB: MAX_FILE_SIZE_MB,
        validateFile: validateFile
    };
});