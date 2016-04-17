$(document).ready(function(){
    var form = $("form.target-update")
    
    $("form.target-update input:submit").click(function(){
        $.post("{{ url_for('osiris.dataset', identifier=dataset.id)}}/target/", form.serialize())
    })
});
