odoo.define('copy_clipboard_extended.basic_fields', function (require) {
  "use strict";

  const basicFields = require('web.basic_fields');

  const CopyClipboard = basicFields.CharCopyClipboard.include({
      events: _.extend({}, basicFields.CharCopyClipboard.prototype.events, {
          'click': '_onClick',
      }),

      _onClick: function (ev) {
          this._super.apply(this, arguments);
          ev.stopPropagation();
      },
  });

  return CopyClipboard;
});
