
function increase(e) {
    var team_id=e.target.id;
    console.log(team_id);
    var score_elem=document.getElementById(team_id);
    var original_count = parseInt(score_elem.value);
    var increased_count = original_count + 1;
    score_elem.value=increased_count;
    score_elem.innerHTML=increased_count;
//    var team_name=this.name;
    //console.log(original_count)
    //console.log(increased_count)
    //});
    
    $.ajax({
      type: "POST",
      url: "/increment",
           data: JSON.stringify({'team_id':team_id,'score':increased_count,'type':team_id+'_score'}),//JSON.stringify(increased_count),
      contentType: "application/json",
      dataType: 'json',
      success: function(result) {
      console.log(result);
      //result['game'][team_id+'_score']=increased_count;
      //console.log(score_elem)
      }
    });
}


function decrease(e) {
    var team_id=e.target.id;
    var aa=team_id.substring(5);
    console.log(aa);
    var score_elem=document.getElementById(aa);
    var original_count = parseInt(score_elem.value);
    var decreased_count = original_count - 1;
    score_elem.value=decreased_count;
    score_elem.innerHTML=decreased_count;
    $.ajax({
      type: "POST",
      url: "/increment",
      data: JSON.stringify({'team_id':aa,'score':decreased_count,'type':team_id+'_score'}),//JSON.stringify(decreased_count), //{'team_name':result.team_names,'scores':result.scores,'increased_count':JSON.stringify(increased_count)},
      contentType: "application/json",
      dataType: 'json',
      success: function(result) {
      //result['game'][aa+'_score']=decreased_count;
      console.log(result);
        //console.log(data)
      }
    });
}

//function save() {
//
//    $.ajax({
//      type: "POST",
//      url: "/save_game",
//      data:JSON.stringify(decreased_count), //{'team_name':result.team_names,'scores':result.scores,'increased_count':JSON.stringify(increased_count)},
//      contentType: "application/json",
//      dataType: 'json',
//      success: function(result) {
//      result['scores'][team_id]=decreased_count;
//      console.log(result);
//        //console.log(data)
//      }
//    });
//}
//
//function game_over() {
//    var team_id=e.target.id;
//    var aa=team_id.substring(5);
//    console.log(aa);
//    var score_elem=document.getElementById(aa);
//    var original_count = parseInt(score_elem.value);
//    var decreased_count = original_count - 1;
//    score_elem.value=decreased_count;
//    score_elem.innerHTML=decreased_count;
//    $.ajax({
//      type: "POST",
//      url: "/game_over",
//      data:JSON.stringify(decreased_count), //{'team_name':result.team_names,'scores':result.scores,'increased_count':JSON.stringify(increased_count)},
//      contentType: "application/json",
//      dataType: 'json',
//      success: function(result) {
//      result['scores'][team_id]=decreased_count;
//      console.log(result);
//        //console.log(data)
//      }
//    });
//}
