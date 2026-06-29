(function () {
  var links = document.querySelectorAll('.locationLink');
  var frame = document.getElementById('contactMapFrame');
  if (!links.length || !frame) return;

  function normalizeDecimal(value) {
    return String(value).replace(',', '.');
  }

  function parseCoords(link) {
    if (link.dataset.lat && link.dataset.lng) {
      return {
        lat: parseFloat(normalizeDecimal(link.dataset.lat)),
        lng: parseFloat(normalizeDecimal(link.dataset.lng)),
      };
    }
    if (link.dataset.cordinates) {
      var match = String(link.dataset.cordinates).match(/^(-?\d+[.,]\d+),(-?\d+[.,]\d+)$/);
      if (match) {
        return {
          lat: parseFloat(normalizeDecimal(match[1])),
          lng: parseFloat(normalizeDecimal(match[2])),
        };
      }
    }
    return null;
  }

  function buildEmbedUrl(lat, lng) {
    return 'https://www.google.com/maps?q=' + lat + ',' + lng + '&hl=uk&z=16&output=embed';
  }

  links.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      links.forEach(function (l) {
        l.classList.remove('active');
      });
      this.classList.add('active');

      var coords = parseCoords(this);
      if (!coords || !coords.lat || !coords.lng) return;
      frame.src = buildEmbedUrl(coords.lat, coords.lng);
    });
  });
}());
