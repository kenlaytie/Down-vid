// JS Methods

function _(id) {
    return document.getElementById(id);
}

const input = _('url');
input.addEventListener('paste', (e) => {

    e.preventDefault();
    input.value = e.clipboardData.getData('text');
    _submit();

});

const title = _('title');
const thumbnail = _('thumbnail');
const color = _('image-color');
const list = _('content');

let isAnalyzing = false;

// Submit

function _submit() {

    if (isAnalyzing == true) return;

    var value = input.value;
    if (value.trim() == '') return;

    _('search-button').classList.add('__load');
    _('error').classList.remove('__show');

    isAnalyzing = true;

    $.ajax({
        url: '/analyze',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            url: value,
        }),
        success: function (responce) {

            _('search-button').classList.remove('__load');
            isAnalyzing = false;
            console.log(responce);

            if (responce.exists == true) {

                title.textContent = responce.title;
                thumbnail.src = responce.thumbnail;
                color.style.background = `rgb(${responce.color[0]}, ${responce.color[1]}, ${responce.color[2]})`;
                list.innerHTML = '';

                responce.formats.forEach(format => {

                    var content = `
                        <tr>
                            <td>${format.type}</td>
                            <td>${format.resolution}</td>
                            <td>${format.filesize}</td>
                            <td>
                                <div class="button">
                                    <button onclick="_download('${responce.title}.${format.ext}', '${format.url}', this)">
                                        <i class="fa-solid fa-spin fa-spinner"></i>
                                        <p>Download</p>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                    list.insertAdjacentHTML('afterbegin', content);

                });

                _('data').classList.add('__show');
                _('data').scrollIntoView({ behavior: "smooth" });

            }
            else {
                _('error').classList.add('__show');
            }

        },
        error: function (error) {

            console.log('Error:', error);
            isAnalyzing = false;
            _('search-button').classList.remove('__load');
            _('error').classList.add('__show');

        }
    });

}

_submit();

// Download

function _download(name, url, target) {

    var parent = target.parentNode;
    parent.classList.add('__load');

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/download';

    var data = {
        'filename': name,
        'url': url,
    };

    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = data[key];
            form.appendChild(input);
        }
    }

    document.body.appendChild(form);
    form.submit();
    form.remove();

    parent.classList.remove('__load');

}