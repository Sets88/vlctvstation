$(document).ready(function(){
	$(document).on('click',".editjob,.addjob,.openmedia,.deletejob,.gethash",function()
	{
		$.ajax({
			url: $(this).attr("href") + "1/",
			type: "GET",
			dataType: "text",
			data: {},
			timeout:30000, 
			async:false,
			cache: false,
			error: function(xhr)
			{
				console.log('Ошибка!'+xhr.status+' '+xhr.statusText);
			},
			success: function(text)
			{
				document.getElementById("myModal").innerHTML=text;
				$("#myModal").modal();
			}
		});
		return false;

	});
	$(document).on('click', ".gethashsubmit", function()
	{
//		alert($("#gethashform").attr("action"));
//			url: $("#gethashform").attr("action") + "1/",
		var dataString = $("#gethashform").serialize();
		$.ajax({
			url: $("#gethashform").attr("action") + "1/",
			type: "POST",
			dataType: "html",
			data: dataString,
			success: function(text)
			{
				document.getElementById("myModal").innerHTML=text
			}
		});
		return false;
	});
});
