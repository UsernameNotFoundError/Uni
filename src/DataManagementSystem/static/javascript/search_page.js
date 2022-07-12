$(document).ready(function(){
  console.log("wow1");
// check and uncheck all when #checkall is cliced
$("#checkall").click(function () {
    if ($("#checkall").is(':checked')) {
        $("input[type=checkbox]").each(function () {
            console.log("wow");
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
        console.log("wow2");
    // Uncheck all if one of .checkthis is uncheked
    if ($(this).is(':checked') == false)
      {
        console.log("This worked");
      $(".allChecked").each(function ()
        {
        $(this).prop("checked", false);
        });
      }
    else
      {
      // check all if one of .checkthis is checked and all other are checked
      console.log("Iam in");
      let checkAll = true;
      $(".checkthis ").each(function ()
          {
            console.log("wow");
          if( $(this).is(':checked') == false)
            {
            console.log("WHAT");
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
console.log("JavaScript working! (result_page.js)");
