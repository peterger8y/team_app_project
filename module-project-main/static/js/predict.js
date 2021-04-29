$(function(){
	$('input').change(function(){
		var location = $('#location').val();
		$.ajax({
			url: '/input',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});