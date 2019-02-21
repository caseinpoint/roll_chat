$(document).ready(function() {
	var chatSocket = new WebSocket(
		'ws://' + window.location.host + '/ws/chat/' + game_id
	);

	chatSocket.onmessage = function(e) {
		let div = document.createElement('div');
		div.className = 'row';

		let data = JSON.parse(e.data);

		// document.title = '*' + data['user_alias'] + '* | Chat+Roll';

		let p1 = document.createElement('p');
		p1.className = 'col-2 px-1 text-right text-truncate';
		p1.innerHTML = '<strong>' + data['user_alias'] + ':</strong>';
		div.appendChild(p1);

		data['content'] = data['content'].split('\n');

		let line_count = 1;
		for (msg of data['content']) {
			let p2 = document.createElement('p');

			if (line_count === 1)	p2.className = 'col-10 px-1';
			else p2.className = 'col-10 offset-2 px-1'
			if (msg.includes('/r') || msg.includes('/R'))
				p2.className += ' text-primary';
			else if (msg.includes('ROLL_RESULT:'))
				p2.className += ' text-success';
			else if (msg.includes('ROLL_ERROR:'))
				p2.className += ' text-danger';

			p2.appendChild(document.createTextNode(msg));
			div.appendChild(p2);
			line_count++;
		}

		$('#chat_msg_box').append(div);

		if (data['user_id'] == user_id) {
			$('#btn_scr_dwn').click();
		} else {
			$('#btn_scr_dwn').html('New Message From ' + data['user_alias']);
			$('#btn_scr_dwn').removeClass('btn-info');
			$('#btn_scr_dwn').addClass('btn-warning');
		}
	}

	chatSocket.onclose = function(e) {
		console.error('chatSocket closed unexpectedly');
	}

	$('#chat_msg_input').keyup(function(e) {
		if (e.originalEvent.keyCode === 13 && e.originalEvent.shiftKey) {
			$('#chat_msg_btn').click();
		}
	});

	$('#chat_msg_btn').click(function() {
		let message = $('#chat_msg_input').val().trim();
		if (message.length === 0) {
			window.alert('Don\'t clutter my beautiful database with empty messages.')
		} else {
			chatSocket.send(JSON.stringify({
				'msg_str': message,
				'game_id': game_id,
				'user_id': user_id
			}));
		}
		$('#chat_msg_input').val('');
	});

	$('#btn_scr_dwn').click(function() {
		$('#chat_msg_box').scrollTop($('#chat_msg_box')[0].scrollHeight);
		if ($('#btn_scr_dwn').hasClass('btn-warning')) {
			$('#btn_scr_dwn').removeClass('btn-warning');
			$('#btn_scr_dwn').addClass('btn-info');
			$('#btn_scr_dwn').html('Scroll To Bottom');
		}
	});

	$('.die-btn').click(function() {
		$('#dice_modal').modal("hide")
		let mod = parseInt($('#modifier').val());
		$('#modifier').val('0');
		if (!mod) {
			var message = '/r 1d' + this.value;
		} else if (mod < 0) {
			var message = '/r 1d' + this.value + mod;
		} else {
			var message = '/r 1d' + this.value + '+' + mod;
		}
		chatSocket.send(JSON.stringify({
			'msg_str': message,
			'game_id': game_id,
			'user_id': user_id
		}));
	});
});
