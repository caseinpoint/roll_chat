$(document).ready(function() {
	var chatSocket = new WebSocket(
		'ws://' + window.location.host + '/ws/chat/' + game_id
	);

	chatSocket.onmessage = function(e) {
		let data = JSON.parse(e.data);
		// console.log(data);

		let div = document.createElement('div');
		div.className = 'row';

		let p1 = document.createElement('p');

		if (data['user_id'] == gm_id && data['content'] == '__END_SESSION__') {
			let div2 = document.createElement('div');
			div2.className = 'col-12'
			div2.appendChild(document.createElement('hr'));
			p1.className = 'text-center text-secondary';
			p1.innerHTML = '<strong>GM ' + data['user_alias'] + ' ended session.</strong>';
			div2.appendChild(p1);
			div2.appendChild(document.createElement('hr'));
			div.appendChild(div2);
		} else {
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
		}


		$('#chat_msg_box').append(div);

		if (data['user_id'] == user_id) {
			$('#btn_scr_dwn').click();
		} else {
			$('#btn_scr_dwn').html('New Message');
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
			window.alert('Please don\'t clutter our database with empty messages.')
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
			$('#btn_scr_dwn').html('Scroll Down');
		}
	});

	$('.die-btn').click(function() {
		$('#dice_modal').modal("hide")
		let mod = parseInt($('#modifier').val());
		$('#modifier').val('0');
		if (!mod) {
			var message = '/roll 1d' + this.value;
		} else if (mod < 0) {
			var message = '/roll 1d' + this.value + mod;
		} else {
			var message = '/roll 1d' + this.value + '+' + mod;
		}
		chatSocket.send(JSON.stringify({
			'msg_str': message,
			'game_id': game_id,
			'user_id': user_id
		}));
	});

	$('#btn_end_session').click(function() {
		chatSocket.send(JSON.stringify({
			'msg_str': '__END_SESSION__',
			'game_id': game_id,
			'user_id': user_id
		}));
	});
});
