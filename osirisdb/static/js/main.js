$(document).ready(function(){
    $('.datatables').each(function(){$(this).dataTable({
    paging: false,
    autoWidth: false
    });
    });
    $('.datatables-compact').each(function(){$(this).dataTable({
    paging: false,
    searching: false,
    info: false
    });
    });
    
});
