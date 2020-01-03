var client_id = '';
var g_redirect_uri = 'http://' + window.location.host + '/callback/'
// constructs authorization request according to spotify api requirements
function auth(cid) {
  client_id = cid;

  var scopes = 'user-read-private user-read-email user-top-read user-read-recently-played';
  var getreq = 'https://accounts.spotify.com/authorize' +
  '?response_type=code' +
  '&client_id=' + client_id +
  (scopes ? '&scope=' + encodeURIComponent(scopes) : '') +
  '&redirect_uri=' + g_redirect_uri + 
  '&show_dialog=true';

  // Sends get request
  window.location.replace(getreq)

};
