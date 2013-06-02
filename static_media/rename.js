
var o_name=''

function show_song(data){
    $('#search_list').html(data);
    $('#search_list > li').click(function(){
	o_name = $(this).text();
	$('#sng').text(o_name);
	$('#search_list').remove();
    });
}


(function($) {
    $(document).ready(function() {
	$('#search_form').submit(function(){
	    o_name = '';
	    var sng = $('#q').val();
	    if(sng==''){
		$('#nfc').html('Query empty.');
		return false;
	    }
	    $.get('/search_result', 'search_song='+sng, show_song, 'text');
	    return false;
	});

	$('#rbutt').click(function(){
	    var nname = $('#sng').text();
	    $.get('rename_song', 'old_name='+o_name+'&new_name='+nname, function(data) {alert(data); $('#sng').remove();}, 'text');
	});

    });

})(jQuery);
