
var client_pl_token = 23;
var cmc=39;

function notify(msg){
    $('#nfc').html(msg);
}

function update_gp(code){
    $('#gpl > li').remove();
    $('#gpl').html(code);
}

function parsexml(xml){
    setTimeout('', 2000);
    var code=$(xml).find('code').text();
    var token=parseInt($(xml).find('token').text());
    var cs=$(xml).find('cs').text();
    var messages = $(xml).find('messages').text();
    var mtoken = parseInt($(xml).find('mtoken').text());
    var cu = $(xml).find('current_user').text();

    if(code==''){
	$('#nfc').html('Nothing new.');
    }
    else if(code=='empty'){
	$('#nfc').html('Playlist is empty');
	$('#nfc').html('Playing pre selected songs.');
    }
    else{
	$('#gpl > dl').remove();
	$('#gpl').html(code);
	$('dd').filter(function(index){
	    if($(this).html()==cs)
		$(this).css('background-color', '#6699ff');
	});
	client_pl_token=token;
	$('dd').click(function(){
	    var owner=$(this).prevAll('dt').first().text();
	    var myself = $('#myself').text();
	    if(owner==myself){
		$(this).fadeOut();
		$.get('remove_song', 'song='+$(this).text(), function(data){ notify(data);$(this).remove(); }, 'text');
	    }
	    else{
		alert('#%*! off!!!');
	    }
	});
    }

    if(messages!=''){
	$('#mesg_area').append(messages);
	cmc=mtoken;
    }
}

function fetch_pl(){
    $.ajax({
	url : "playlist_updated",
	data : "client_pl_token="+client_pl_token+'&cmc='+cmc,
	success : parsexml,
	dataType : "xml",
	async : false
    });
    
    setTimeout('fetch_pl()', 2000);
}
function add_to_playlist(sng){
    var data = 'song_name='+sng;
    $.get('append_to_playlist', data,
	  function(data){
	      if(data!='redundant'){
		  notify(sng+' '+data);
	      }
	      else{
		  notify(data);
	      }
	  },'text');
}

function search_result_click(sng){
    if(sng!='I am Disappointed with results!')
	add_to_playlist(sng);
    $('#search_list > li').fadeOut('slow').delay(1000).remove();
}

function show_search_result(data){
    if(data==''){
	$('#nfc').html('No search results found.');
	return true;
    }
    data+='<li>I am Disappointed with results!</li>';
    $('#search_list').html(data).hide().fadeIn('slow');
    $('#search_list > li').hover(
	function() {
	    bc = $(this).css('background-color');
	    $(this).css('background-color', '#56afec');
	},
	function() {$(this).css('background-color', bc);}
    );
    $('#search_list > li').click(function(){
	search_result_click($(this).text());
    });
}

function tryremoving(){
    var owner=$(this).prevAll('dt').first().text();
    var myself = $('#myself').text();
    if(owner==myself){
	// delete it...
	$(this).fadeOut();
	var $proxy = null;
	$(proxy) = $(this);
	var s=$(this).text();
	$.get('remove_song', 'song='+s, function(data){ notify(data);$proxy.remove(); }, 'text');
    }
    else{
	alert('Do not interfere in other\'s life!');
    }
}

function decorate(){
    $('#sp > li').click( function() {
	var sname = $(this).text();
	var data = 'song_name='+sname;
	add_to_playlist(sname);
	$(this).fadeOut();
    });
    $('#sp > li').hover(
	function() {
	    bc = $(this).css('background-color');
	    $(this).css('background-color', '#56a5ec');
	},
	function() {$(this).css('background-color', bc);}
    );
}

(function($) {
    $(document).ready(function() {
	client_pl_token = 0;
	fetch_pl();
        var bc='';

	var tp=0,bp=30;
	var ft=0;
	var pb=1;
	
	$('#prevb').click(function(){
	    if(tp==0) return;
	    $.get('gpb', 'batch='+tp, function(data){
		if(data==''){
		    notify('You have reached start of songs sool');
		    return true;
		}
		
		$('#sp > li').remove();
		$('#sp').html(data);

		decorate(); // includes duplicate code
		tp-=30;
		bp-=30;		
	    },'text');

	});

	// if next button is pressed
	$('#nextb').click(function(){
	    $.get('gnb', 'batch='+bp, function(data){
		if(data==''){
		    notify('You have reached end of list');
		    return true;
		}
		
		$('#sp > li').remove();
		$('#sp').html(data);

		decorate(); // includes duplicate code
		tp+=30;
		bp+=30;
	     },'text');
	});

	// if previous button is pressed
	$('#mesg_form').submit(function(){
	    var m = $('textarea').val();
	    if(m=='') return false;

	    $.get('receive_message', 'mesg='+m,'text');
	    
	    $('textarea').val('');
	    return false;
	});
	
	$('#search_form').submit(function(){
	    var sng = $('#q').val();
	    if(sng==''){
		$('#nfc').html('Query empty.');
		return false;
	    }
	    $.get('/search_result', 'search_song='+sng, show_search_result, 'text');
	    return false;
	});

	$('#sp > li, #search_list > li, dd').hover(
	    function() {
		bc = $(this).css('background-color');
		$(this).css('background-color', '#56a5ec');
	    },
	    function() {$(this).css('background-color', bc);}
	);
	
	$('#sp > li').click( function() {
	    var sname = $(this).text();
	    var data = 'song_name='+sname;
	    add_to_playlist(sname);
	    $(this).fadeOut();
	});

    });

})(jQuery);

