function AutoRefresh() {
    var mylink = window.location.href;
    var baselink = mylink.split("#",2)[0];

    document.getElementById("profile_id").href=baselink;
    document.getElementById("chat").href=baselink + "/chat/0";
    document.getElementById("frnd").href=baselink + "/myfrnd";
    document.getElementById("findfrnd").href=baselink + "/findfrnd";
    
}