$(document).ready(function(){
// check and uncheck all when #checkall is cliced
$("#checkall").click(function () {
        if ($("#checkall").is(':checked')) {
            $("input[type=checkbox]").each(function () {
                $(this).prop("checked", true);
            });

        } else {
            $("input[type=checkbox]").each(function () {
                $(this).prop("checked", false);
            });
        }
    });

// Uncheck all if one of .checkthis is uncheked
$(".checkthis").click(function ()
    {
    // Uncheck all if one of .checkthis is uncheked
    if ($(this).is(':checked') == false)
      {
      $(".allChecked").each(function ()
        {
        $(this).prop("checked", false);
        });
      }
    else
      {
      // check all if one of .checkthis is checked and all other are checked
      let checkAll = true;
      $(".checkthis ").each(function ()
          {
          if( $(this).is(':checked') == false)
            {
            checkAll = false;
            };
          }
        );
      if (checkAll)
        {
        $(".allChecked").each(function ()
          {
          $(this).prop("checked", true);
          });
        };
      };
    });

    $("[data-toggle=tooltip]").tooltip();
});

// for copy
function copyThis() {
  var html = $('#text_to_copy').get(0).innerHTML;
  navigator.clipboard.writeText(html);
  /* Alert the copied text */
  //alert("Copied the text: " + html);
}
console.log("JavaScript working! (my_space_page.js)");
