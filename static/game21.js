
	  $("#playeractions").hide()
	  $("div.multiplayerform").hide()
	  $("button.startmultplayergame").hide()
	  $( 'button.exitgame' ).hide()
	  $( 'div.bettingform' ).hide()
	  $( 'div.gamearea' ).hide()
	  //$("div#multiplayer-dropdown").hide()
	  
      var socket = io.connect('127.0.0.1:88');
      socket.on( 'connect', function() {
	    //alert(socket.io.engine.id)
        socket.emit( 'connected', {
          data: 'User Connected'
        } )
		
	$("button.gamechoose").click(function() {
		$("div.gamechoose").hide()		
		if($(this).val() == 'singleplayer') {
			startgame('singleplayer')			
			$("div.deck_box_1").removeClass("col").addClass("col-centered");			
		}
		else
		{			
			$("div.gamechoose").hide()
			$("div.multiplayerform").show()			
		}
	});
	
	$("button.createmultplayergame").click(function() {
		$('input#pid').val($( 'input#player_name' ).val())
		$( 'div.gamestartform' ).hide()
		$( 'div.gamearea' ).show()
		$("button.startmultplayergame").show()		
	    startgame('multiplayer')				
	});
	
	$("button.startmultplayergame").click(function() {		
	    $( 'div.bettingform' ).hide()		
		$( 'button.exitgame' ).show()
		$( 'button.startmultplayergame' ).hide()		
		$( 'div.deck_player' ).empty()
		  $( 'div.deck_player2' ).empty()
		  $( 'div.deck_house' ).empty()		        
		  let player_name = $( 'input#player_name' ).val()		  
		  let gameid = $( 'input#gameid' ).val()		  
		  $( 'input#pid' ).val(player_name)		  
		  $( 'input#gametype' ).val(gametype)
		  
		  socket.emit( 'start_multiplayer_game', {
			player_name : player_name,			
			game_type: gametype,
			gameid: gameid
		  
		} )
	});
	
	$("button.exitgame").click(function() {
		$('div.multiplayerform').hide()
		$( 'div.gamestartform' ).show()
		$("div.gamechoose").show()
		$( 'button.exitgame' ).hide()
		$( 'div.bettingform' ).hide()
		$( 'div.gamearea' ).hide()

		socket.emit( 'exit_game', {
			player_name : $( 'input#player_name' ).val(),
			gameid: $( 'input#gameid' ).val()
		  
		} )		
	});
	
	function startgame(gametype) {	
		$( 'div.bettingform' ).hide()		
		$( 'button.exitgame' ).show()			
		$( 'div.deck_player' ).empty()
		  $( 'div.deck_player2' ).empty()
		  $( 'div.deck_house' ).empty()		        
          let player_name = $( 'input#player_name' ).val()		  
		  $( 'input#pid' ).val(player_name)		  
		  $( 'input#gametype' ).val(gametype)		  
          socket.emit( 'addfirstplayer', {
            player_name : player_name,			
			game_type: gametype
          
        } )		
	}
	
        $("button.start").click( function( e ) {		 
		  $( 'div.deck_player' ).empty()
		  $( 'div.deck_player2' ).empty()
		  $( 'div.deck_house' ).empty()		  		  
          e.preventDefault()
          let player_name = $( 'input#player_name' ).val()
		  let player_bet = $( 'input#bet_amount' ).val()		  
		  $( 'input#pid' ).val(player_name)		  
		  gametype = $('input#multiplayer').is(":checked") ? 'multiplayer' : 'singleplayer'
		  $( 'input#gametype' ).val(gametype)		  
          socket.emit( 'addfirstplayer', {
            player_name : player_name,
			bet_amount : player_bet,			
			game_type: gametype
          } )          
        } )
      } )

	  $("button.bet").click( function( e ) {
          e.preventDefault()
          let player_name = $( 'input#player_name' ).val()
		  let player_bet = $( 'input#bet_amount' ).val()
		  let gameid = $( 'input#gameid' ).val()		  		  
		  
          socket.emit( 'place_bet', {
            player_name : player_name,
			bet_amount : player_bet,
			gameid : gameid
          } )          
        } )      
	  
	  
	  $("body").on('click', '.dropdown-item', function () {
			//alert($(this).val())
		  $( 'div.deck_player' ).empty()
		  $( 'div.deck_player2' ).empty()
		  $( 'div.deck_house' ).empty()
			$( 'div.bettingform' ).hide()
			$( 'div.gamestartform' ).hide()
		$( 'div.gamearea' ).show()			
		  gameid = $(this).attr('value') //.text()
          //e.preventDefault()
          let player_name = $( 'input#player_name' ).val()
		  let player_bet = $( 'input#bet_amount' ).val()
		  $( 'input#gameid' ).val(gameid)
		  $( 'input#pid' ).val(player_name)
		  $( 'input#gametype' ).val('multiplayer')
          socket.emit( 'join_game', {
            player_name : player_name,
			bet_amount : player_bet,
			gameid : gameid
          } )
	  })
	  
	  $("button.multigameselect").click( function( e ) {		
	  e.preventDefault()
		  let player_name = $( 'input#player_name' ).val()
		  let player_bet = $( 'input#bet_amount' ).val()	  
          socket.emit( 'list_multiplayer_games', {
            player_name : player_name,
			bet_amount : player_bet
          } )
      } )
	  
	  $("button.action").click(function(e) {		    
			e.preventDefault()
			  let player_name = $( 'input#player_name' ).val()			  
			  socket.emit( 'player_move', {
				gameid: $( 'input#gameid' ).val(),
				player_name : player_name,
				action: $(this).val()
			  } )
		});
		
	  socket.on( 'player_move', function( msg ) {        
		obj = JSON.parse(msg)		
        updateCards(obj)		
      })
		
	  socket.on( 'start_betting', function( msg ) {
		$( 'button.exitgame' ).show()
		$( 'div.gamearea' ).show()
		$( 'div.output' ).empty()
		// alert(msg)
		$( 'div.gamestartform' ).hide()
		obj = JSON.parse(msg)		
		addPlayersContainer(obj.players)
		$( 'input#gameid' ).val(obj.gameid)
		updatePlayersTitle(obj)
        updateCards(obj)		
		updateBetForm(obj)		
      })
	  
	  socket.on( 'player_exited', function( msg ) {
		  obj = JSON.parse(msg)
		  $("#playeractions").hide()
		  $( 'div.bettingform' ).hide()
		$( 'div.output' ).append( '<div>'+obj.msg+' exited the game. Game will restart.</div>' )
      })
	  
      socket.on( 'my response', function( msg ) {
        console.log( msg )
        if( typeof msg.player_name !== 'undefined' ) {          
          $( 'div.output' ).append( '<div>'+msg.player_name+' '+msg.message+'</div>' )
        }
      })
	  
	  socket.on( 'wait_others', function( msg ) {  
		$( 'div.output' ).append( '<div>After all the players have joined press \"Start game\".</div>' )
		obj = JSON.parse(msg)
		$( 'input#gameid' ).val(obj.gameid)
		$("#playeractions").hide()		
      })
	  
	  socket.on( 'player_joined', function( msg ) {  
		obj = JSON.parse(msg)
		//alert(obj.gameactive)		
		console.log('Player joined. Gameactive='+obj.gameactive+', obj.players.length='+obj.players.length+'obj.observers='+obj.observers)
		if(!obj.gameactive)
		{
			$( 'div.output' ).append( '<div> '+obj.players[obj.players.length-1].name+' joined</div><div>Waiting on '+obj.players[0].name+' to start game ...</div>')					
		}
		else if(obj.observers && obj.observers.length>0)
		{
			$( 'div.output' ).append( '<div> '+obj.observers[obj.observers.length-1].name+' joined and waiting until the current round ends</div>' )
			
		}
		
      })
	  
	  socket.on( 'game_start', function( msg ) {		
		$( 'div.bettingform' ).hide();
		obj = JSON.parse(msg)		
        if( typeof obj.players !== 'undefined' ) {		 
		  multiplayer = obj.players.length > 1
		  myturn = $('input#pid').val() == obj.player_turn
          //$( 'div.output' ).append( '<div>'+(multiplayer ? 'Multiplayer' : 'Singleplayer')+' game start</div><div>'+(myturn ? 'my' : obj.player.name)+' turn</div>' )
		$( 'input#gameid' ).val(obj.gameid)
		updateCards(obj)		
        }
      })
	  function updatePlayersTitle(obj)
	  {
		  multiplayer = obj.players.length > 1
		  names = obj.players[0].name // first player
		  if(multiplayer)
		  {
			  for(pindex=1;pindex<obj.players.length;pindex++)
			  {
				names += ", "+obj.players[pindex].name  
			  }
			  
		  }
		  $("h3.game-players").text(names +" vs House")
	  }
	  function updateCards(obj) {
		  
	    
	    multiplayer = obj.players.length > 1
		myturn = $('input#pid').val() == obj.player_turn
		
		generateInfoSpan($( 'div.deck_house_info' ), obj.house)
		for(pindex=0;pindex<obj.players.length;pindex++)
		{
			addCards(obj.players[pindex].hand, $( 'div.deck_player_'+(pindex+1) ), false, !multiplayer)
			generateInfoSpan($( 'div.deck_player_info_'+(pindex+1) ), obj.players[pindex])			
		}
		
		if(myturn)
		{
			$("#playeractions").show()
			$("div.output").text("Please choose Hit or Stand.")
		}
		else
		{
			$("#playeractions").hide()
			$("div.output").text("Waiting on other players ...")
		}		
		
		if(!obj.game_state)
		{	
			$("div.output").text("Round is over. "+obj.msg)
			$("#playeractions").hide()	
					
			addCards(obj.house.hand, $( 'div.deck_house' ), false, true)			
			countdownrestartgame(obj, 6)
			
		}
		else
		{
			addCards(obj.house.hand, $( 'div.deck_house' ), obj.house.hand.length == 2, true)				
			
		}

	}
	
	socket.on( 'display_multiplayer_games', function( msg ) {
		
	   obj = JSON.parse(msg)	
		// $( 'div.output' ).append( '<div><b style="color: #000">'+obj.games+'</div>' )
		$("#playeractions").hide()	
		
		$("div.dropdown-menu").empty()
		for(i=0;i<obj.games.length;i++)
		{
			g = obj.games[i]
			n = obj.names[i]
			$("div.dropdown-menu").append("<a class=\"dropdown-item\" value=\""+g+"\">"+n+"</a>")
		}		
		$("div#multiplayer-dropdown").show()
      })	  
	 
	function countdownrestartgame(obj, delaysecs)
	{
		counter=delaysecs
		i = window.setInterval(function(){
			if(counter <= (delaysecs-1))
			{
					$("div.output").text("Next round in "+counter+" secs ...")
			}			  
		  counter--			 
		}, 1000);
		
		setTimeout(
		  function() 
		  {
			  window.clearInterval(i) 
			  
			  $( 'div.deck_player' ).empty()
			  $( 'div.deck_player2' ).empty()
			  $( 'div.deck_house' ).empty()
			  // $( 'div.output' ).empty()
			  
			  if($('input#pid').val() == obj.players[0].name)
			  {				  
				  socket.emit( 'game_restart', {					
					gameid : obj.gameid
				} )
			  }
			  
		  }, delaysecs*1000);
	}
	function generateInfoSpan(info_div, player)
	{
		info_div.empty()
		addbadge = ""
		if(player.points == 21)
			addbadge = "<span class=\"badge badge-pill badge-warning\" style=\"font-size: 1.0rem;\"> 21 </span>"
		else if(player.points > 21)
			addbadge = "<span class=\"badge badge-pill badge-dark\" style=\"font-size: 1.0rem;\"> BUST </span>"
		if(player.name != "house")
		{
			info_div.append(player.name+"<br /><span class=\"badge badge-secondary\">"+player.bet_amount+"€ ("+player.money+"€)</span> "+addbadge)
		}
		else
		{
			info_div.append(player.name+"<br /><span class=\"badge badge-secondary\">"+player.money+"€</span> "+addbadge)
		}
		
	}
	function addCards(hand, containerDiv, hideLast, horizontal)
	{	
		containerDiv.empty()
		for(i=0;i<hand.length;i++)
		{
			if(hideLast && (i == hand.length-1))
			{
				card = createCard(hand[-1])
			}
			else
			{
				card = createCard(hand[i])				
			}
			card.style.position = "absolute";
			//card.style.zIndex = "-1";
			if(!horizontal)
			{
				card.style.top = (i*1.5).toString()+"rem";
			}
			else{
				card.style.left = (i*1.4).toString()+"rem";
			}			
			containerDiv.append(card);				
		}
	}
	
	
	function updateBetForm(obj) {	    
		myturntobet = $('input#pid').val() == obj.betting_turn
		
		if(myturntobet)
		{
			$( 'div.bettingform' ).show();
			$("div.output").text("Please enter your bet amount.")
		}
		else
		{
			$( 'div.bettingform' ).hide();
			$("div.output").text("Waiting on other players to place their bets ...")
		}		
	}
	
	function addPlayersContainer(players)
	{
		players_div = $( 'div.players_container' )
		players_div.empty()
		if(players)		
		{
			position_class = "col-centered"
			/*if(players.length == 1)
			{
					position_class = "col-centered"
			}*/
			for(pindex=0;pindex<players.length;pindex++)
			{
				console.log('Adding container for player '+players[pindex].name);
				player_box = '<div class=\"deck_box '+position_class+' deck_box_'+(pindex+1)+'\"><div class=\"deck_player_info deck_player_info_'+(pindex+1)+'\"></div><div class=\"deck_player deck_player_'+(pindex+1)+'\" style=\"position:relative\"></div>'
				players_div.append(player_box)
			}
		}
	else{ return }
	}
	
