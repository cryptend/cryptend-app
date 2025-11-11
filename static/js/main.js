function addLoading(formId) {
  let form = document.getElementById(formId);
  if (form) {
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      let btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.querySelector('span').remove();
      btn.querySelector('.loading').classList.remove('hidden');
      form.submit();
    });
  }
}

addLoading('create-chat-form');
addLoading('encrypt-form');
addLoading('decrypt-form');

function copyText(btnId, inputId) {
  let btn = document.getElementById(btnId);
  let input = document.getElementById(inputId);
  if (btn && input) {
    btn.addEventListener('click', function() {
      let text = input.value;
      if (text) {
        navigator.clipboard.writeText(text).then(() => {
          let btnText = btn.innerText;
          btn.innerText = 'Copied';
          setTimeout(() => {
            btn.innerText = btnText;
          }, 1000);
        });
      }
    });
  }
}

copyText('copy', 'output');
copyText('copy-1', 'output-1');
copyText('copy-2', 'output-2');

if (window.location.pathname.slice(0, 2) === '/3') {
  window.scrollTo(0, document.body.scrollHeight);
}