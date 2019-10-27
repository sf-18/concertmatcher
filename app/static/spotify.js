var client_id = '';
var g_redirect_uri = 'http://' + window.location.host + '/callback/'
function auth(cid) {
  client_id = cid;

  var scopes = 'user-read-private user-read-email';
  var getreq = 'https://accounts.spotify.com/authorize' +
  '?response_type=code' +
  '&client_id=' + client_id +
  (scopes ? '&scope=' + encodeURIComponent(scopes) : '') +
  '&redirect_uri=' + g_redirect_uri;

  // Sends get request
  window.location.replace(getreq)

};
