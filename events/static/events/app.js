function shareEvent(title, text, url) {
  if (navigator.share) {
    navigator
      .share({
        title: title,
        text: text,
        url: url,
      })
      .then(() => console.log("Successful share"))
      .catch((error) => console.log("Error sharing", error));
  }
}

// Split strings that contain emojis. This is used to display the emojis in the confetti.
function splitEmojiString(str) {
  if (Intl.Segmenter) {
    // Chrome, Edge, Safari
    return Array.from(new Intl.Segmenter().segment(str)).map(x => x.segment);
  } else {
    // Firefox, does poorly characters that are 4-bytes in utf8 like 🇺🇸
    return Array.from(str);
  }
}

var jsConfetti = null;

// Use this for testing the confetti.
function launchConfetti(emojisString, confettiAmount) {
  if (jsConfetti === null) {
    jsConfetti = new JSConfetti();
  }
  jsConfetti.addConfetti({
    "emojis": splitEmojiString(emojisString),
    "confettiNumber": confettiAmount,
  });
}

function previewLocation(container, location) {
  var mapsUrl = "https://maps.google.com/maps?width=100%25&amp;height=400&amp;hl=en&amp;q=" + encodeURIComponent(location) + "&amp;t=&amp;z=14&amp;ie=UTF8&amp;iwloc=B&amp;output=embed";
  var embedHtml = '<div class="location-preview"><iframe width="100%" height="400" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="' + mapsUrl + '"></iframe></div>';
  container.innerHTML = embedHtml;
}
