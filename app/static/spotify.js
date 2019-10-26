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

// // Extracts auth code from response url and retrieves access token
// window.onhaschange = () => {
//   var path = window.location.href;
//   if (path.includes(g_redirect_uri)) {
//     parsed_url = parseURL(path);
//     // If code exists in response url, send post request to retrieve token
//     var code = parsed_url.searchObject['code'];
//     var state = parsed_url.searchObject['state']
//     if (typeof code != 'undefined') {
//       const request = new XMLHttpRequest();
//       request.open("POST", 'https://accounts.spotify.com/api/token');
//       request.setRequestHeader('Authorization', btoa(client_id));
//
//       // var postreq = 'https://accounts.spotify.com/api/token' +
//       // '?grant_type=authorization_code' +
//       // '&code=' + code +
//       // '&redirect_uri' + redirect_uri;
//       request.onload = () => {
//         response = JSON.parse(response.responseText);
//         alert('access token: ' + response['access_token'])
//       };
//
//       const data = new FormData();
//       data.append("grant_type", "authorization_code");
//       data.append("code", code);
//       data.append("redirect_uri", p_redirect_uri);
//
//       request.send(data);
//     }
//     else {
//       alert('auth code does not exist.')
//     }
//   }
// };


function parseURL(url) {
    var parser = document.createElement('a'),
        searchObject = {},
        queries, split, i;
    // Let the browser do the work
    parser.href = url;
    // Convert query string to object
    queries = parser.search.replace(/^\?/, '').split('&');
    for( i = 0; i < queries.length; i++ ) {
        split = queries[i].split('=');
        searchObject[split[0]] = split[1];
    }
    return {
        protocol: parser.protocol,
        host: parser.host,
        hostname: parser.hostname,
        port: parser.port,
        pathname: parser.pathname,
        search: parser.search,
        searchObject: searchObject,
        hash: parser.hash
    };
}
