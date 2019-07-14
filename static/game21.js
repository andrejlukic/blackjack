
	  $("#playeractions").hide()
	  $("div.multiplayerform").hide()
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
			$("div.deck_box_2").remove()
			$("div.deck_box_1").removeClass("col-left").addClass("col-centered");			
		}
		else
		{			
			$("div.gamechoose").hide()
			$("div.multiplayerform").show()			
		}
	});
	
	$("button.startmultplayer").click(function() {
		$("div.gamechoose").hide()	
	    startgame('multiplayer')				
	});
	
	$("button.exitgame").click(function() {
		$('div.multiplayerform').hide()
		$( 'div.gamestartform' ).show()
		$("div.gamechoose").show()
		$( 'button.exitgame' ).hide()
		$( 'div.bettingform' ).hide()
		$( 'div.gamearea' ).hide()		
	});
	
	function startgame(gametype) {	
		$( 'div.bettingform' ).hide()
		$( 'div.gamearea' ).show()	
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
		updateInfo(obj)		
      })
		
	  socket.on( 'start_betting', function( msg ) {
		$( 'button.exitgame' ).show()
		$( 'div.output' ).empty()
		// alert(msg)
		$( 'div.gamestartform' ).hide()
		
		obj = JSON.parse(msg)		
		$( 'input#gameid' ).val(obj.gameid)
		updatePlayersTitle(obj)
        updateCards(obj)
		updateInfo(obj)
		updateBetForm(obj)		
      })
	  
      socket.on( 'my response', function( msg ) {
        console.log( msg )
        if( typeof msg.player_name !== 'undefined' ) {          
          $( 'div.output' ).append( '<div>'+msg.player_name+' '+msg.message+'</div>' )
        }
      })
	  
	  socket.on( 'wait_others', function( msg ) {  
		$( 'div.output' ).append( '<div>waiting for others to join ...</div>' )
		$("#playeractions").hide()		
      })
	  
	  socket.on( 'game_start', function( msg ) {		
		$( 'div.bettingform' ).hide();
		obj = JSON.parse(msg)		
        if( typeof obj.player !== 'undefined' ) {		 
		  myturn = $('input#pid').val() == obj.player.name
		  multiplayer = obj.player2 != null
          //$( 'div.output' ).append( '<div>'+(multiplayer ? 'Multiplayer' : 'Singleplayer')+' game start</div><div>'+(myturn ? 'my' : obj.player.name)+' turn</div>' )
		$( 'input#gameid' ).val(obj.gameid)
		updateCards(obj)
		updateInfo(obj)
        }
      })
	  function updatePlayersTitle(obj)
	  {
		  multiplayer = obj.player2 != null
		  names = obj.player.name
		  if(multiplayer)
		  {
			  names += "& "+obj.player2.name
		  }
		  $("h3.game-players").text(names +" vs House")
	  }
	  function updateCards(obj) {
	    //alert(obj)
	    multiplayer = obj.player2 != null
		myturn = $('input#pid').val() == obj.player_turn
		mefirst = !multiplayer || $('input#pid').val() == obj.player.name
		
		
		$( 'div.deck_player' ).empty()
		$( 'div.deck_player2' ).empty()
		$( 'div.deck_house' ).empty()
		$("#playeractions").hide()
		
		if(mefirst)
		{
			addCards(obj.player.hand, $( 'div.deck_player' ), false, !multiplayer)			
			
			if(multiplayer)
			{
				addCards(obj.player2.hand, $( 'div.deck_player2' ), false, !multiplayer)				
			}
						
		}
		else
		{
			addCards(obj.player.hand, $( 'div.deck_player2' ), false, !multiplayer)
			addCards(obj.player2.hand, $( 'div.deck_player' ), false, !multiplayer)			
		}
		//$( 'div.deck_house' ).append(createCard(obj.house.hand[0]));		
		
		if(myturn)
		{
			$("#playeractions").show()
			$("div.output").text("Please choose Hit or Stand.")
		}
		else
		{
			$("div.output").text("Waiting on other players ...")
		}		
		
		if(!obj.game_state)
		{	
			$("div.output").text("Round is over. "+obj.msg)
			$("#playeractions").hide()	
					
			addCards(obj.house.hand, $( 'div.deck_house' ), false, true)
			
			counter=6
			i = window.setInterval(function(){
				if(counter <= 5)
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
				  
				  if(mefirst)
				  {				  
					  socket.emit( 'game_restart', {					
						gameid : obj.gameid,
						bet: $( 'input#bet_amount' ).val() // that's a hack because the GUI for taking bets every round is not there yet
					} )
				  }
				  
			  }, 6000);
			
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
	  
	  function updateInfo(obj) {
	    //alert(obj)
	    multiplayer = obj.player2 != null
		myturn = $('input#pid').val() == obj.player_turn
		mefirst = !multiplayer || $('input#pid').val() == obj.player.name
		
		
		$( 'div.deck_player_info' ).empty()
		$( 'div.deck_player2_info' ).empty()
		$( 'div.deck_house_info' ).empty()
		//$("div.output").empty()
		
		if(mefirst)
		{
			// $( 'div.deck_player_info' ).append(obj.player.name+'<span class=\"badge\">'+obj.player.money+'€</span>')
			generateInfoSpan($( 'div.deck_player_info' ), obj.player)
			if(multiplayer)
			{
				generateInfoSpan($( 'div.deck_player2_info' ), obj.player2)				
			}
		}
		else
		{
			generateInfoSpan($( 'div.deck_player2_info' ), obj.player)			
			if(multiplayer)
			{
				generateInfoSpan($( 'div.deck_player_info' ), obj.player2)				
			}
		}
		
		if(myturn)
		{
			$( 'div.deck_player_info' ).addClass("myturn");
		}
		else
		{
			$( 'div.deck_player_info' ).removeClass("myturn");
		}
		
		generateInfoSpan($( 'div.deck_house_info' ), obj.house)		
	}	
	
	function generateInfoSpan(div, player)
	{
		addbadge = ""
		if(player.points == 21)
			addbadge = "<span class=\"badge badge-pill badge-warning\" style=\"font-size: 1.3rem;\"> 21 </span>"
		else if(player.points > 21)
			addbadge = "<span class=\"badge badge-pill badge-dark\" style=\"font-size: 1.3rem;\"> BUST </span>"
		if(player.name != "house")
		{
			div.append(player.name+"<br /><span class=\"badge badge-secondary\">"+player.bet_amount+"€ ("+obj.player.money+"€)</span> "+addbadge)
		}
		else
		{
			div.append(player.name+"<br /><span class=\"badge badge-secondary\">"+obj.player.money+"€</span> "+addbadge)
		}
		
	}
	function addCards(hand, containerDiv, hideLast, horizontal)
	{
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
	
