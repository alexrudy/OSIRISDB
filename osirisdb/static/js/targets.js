$(document).ready(function(){
    
    var setup_form = function(index){
        var form = $(this)
        var target = form.attr('action')
        form.on('submit', function(event){
            var form = $(this)
            form.find('input#prev').val('none')
            event.preventDefault()
            $.post(target, form.serialize()).done(function(){
                $.get(target + "_row/", function(data) {
                    cell = form.parents("td")
                    cell.empty().html(data)
                    cell.find("form.target-update").each(setup_form)
                })
            })
        })
    }
    $("form.target-update").each(setup_form)
});
