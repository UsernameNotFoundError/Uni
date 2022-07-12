$(document).ready(function(){
// check and uncheck all when #checkall is cliced
$("#mytable #checkall").click(function () {
        if ($("#mytable #checkall").is(':checked')) {
            $("#mytable input[type=checkbox]").each(function () {
                $(this).prop("checked", true);
            });

        } else {
            $("#mytable input[type=checkbox]").each(function () {
                $(this).prop("checked", false);
            });
        }
    });

// Uncheck all if one of .checkthis is uncheked
$("#mytable .checkthis").click(function ()
    {
    // Uncheck all if one of .checkthis is uncheked
    if ($(this).is(':checked') == false)
      {
      $("#mytable  #checkall").each(function ()
        {
        $(this).prop("checked", false);
        });
      }
    else
      {
      // check all if one of .checkthis is checked and all other are checked
      let checkAll = true;
      $("#mytable .checkthis ").each(function ()
          {
          if( $(this).is(':checked') == false)
            {
            checkAll = false;
            };
          }
        );
      if (checkAll)
        {
        $("#mytable  #checkall").each(function ()
          {
          $(this).prop("checked", true);
          });
        };
      };
    });

    $("[data-toggle=tooltip]").tooltip();

// download button
$("#mytable #checkall").click(
  function(){

    }
  );
// for table
});
// for copy
function copyThis() {
  var html = $('#text_to_copy').get(0).innerHTML;
  navigator.clipboard.writeText(html);
  /* Alert the copied text */
  //alert("Copied the text: " + html);
}
console.log("JavaScript working! (result_page.js)");
