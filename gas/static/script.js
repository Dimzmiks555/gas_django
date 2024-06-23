

const OBJECT_DICT = {
    'type_of_building': '',
    'region': 'region',
    'area': 'area',
    'type_of_city': '',
    'city': 'city',
    'street_type': 'street_type',
    'street': 'street',
    'house': 'house',
    'room': '',
    'postcode': 'postal_code',
}

function maskPhone(selector, masked = '+7 (___) ___-__-__') {
	const elems = document.querySelectorAll(selector);

	function mask(event) {
		const keyCode = event.keyCode;
		const template = masked,
			def = template.replace(/\D/g, ""),
			val = this.value.replace(/\D/g, "");
		console.log(template);
		let i = 0,
			newValue = template.replace(/[_\d]/g, function (a) {
				return i < val.length ? val.charAt(i++) || def.charAt(i) : a;
			});
		i = newValue.indexOf("_");
		if (i !== -1) {
			newValue = newValue.slice(0, i);
		}
		let reg = template.substr(0, this.value.length).replace(/_+/g,
			function (a) {
				return "\\d{1," + a.length + "}";
			}).replace(/[+()]/g, "\\$&");
		reg = new RegExp("^" + reg + "$");
		if (!reg.test(this.value) || this.value.length < 5 || keyCode > 47 && keyCode < 58) {
			this.value = newValue;
		}
		if (event.type === "blur" && this.value.length < 5) {
			this.value = "";
		}

	}

	for (const elem of elems) {
		elem.addEventListener("input", mask);
		elem.addEventListener("focus", mask);
		elem.addEventListener("blur", mask);
	}
	
}


document.addEventListener("DOMContentLoaded", () => {
    
    let objectHelper = document.querySelector('.object_address_helper')
    let regAddressHelper = document.querySelector('.reg_address_helper')
    let objectResultsBlock = document.querySelector('.object_address_helper_results')
    let regAddressResultsBlock = document.querySelector('.reg_address_helper_results')

    maskPhone('#id_number')

    function cleanResults() {
        objectResultsBlock.innerHTML = ""
        regAddressResultsBlock.innerHTML = ""
    }

    function setObjectValues(result) {
        for (let value of Object.entries(OBJECT_DICT)) {

            let field = document.querySelector(`#id_${value[0]}`)

            if (value[0] == 'type_of_city') {
                field.value = result['city_type_full'] || result['settlement_type_full']
            } else if (value[0] == 'room') {
                if (result['flat']) {
                    field.value = result['flat']
                }
            } else if (value[0] == 'type_of_building') {
                if (result['flat']) {
                    field.value = "Квартира"
                } else {
                    field.value = "Дом"
                }
            } else {
                field.value = result[value[1]]
            }

        }
    }

    function setRegAddressValue(result) {
        let field = document.querySelector('#id_registration_adress')
        field.value = result
    }

    async function getAddressFromDaData(query) {
        var url = "http://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address";
        var token = "cccd906b9f52be8f1ee449484885f4327766041c";

        var options = {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Token " + token
            },
            body: JSON.stringify({query: query})
        }

        return fetch(url, options)
        .then(response => response.json())
        .then(result => result)
        .catch(error => console.log("error", error));
    }

    function selectResult(result, type) {
        cleanResults()
        if (type == 'OBJECT') {
            objectHelper.value = result?.value
            setObjectValues(result?.data)
        } else {
            regAddressHelper.value = result?.value
            setRegAddressValue(result?.value)
        }
    }

    function renderResults(results, type) {

        cleanResults()

        console.log(results)

        results.forEach(result => {
            let result_div = document.createElement('div')
            result_div.classList.add('helper_result');
            result_div.innerHTML = result?.value
            result_div.addEventListener('click', (e) => {
                selectResult(result, type)
            })
            if (type == 'OBJECT') {
                objectResultsBlock.appendChild(result_div);
            } else {
                regAddressResultsBlock.appendChild(result_div);
            }
        });
    }



    objectHelper.addEventListener('input', async (e) => {
        let results = await getAddressFromDaData(e.target.value)
        renderResults(results?.suggestions, 'OBJECT')
    })
    regAddressHelper.addEventListener('input', async (e) => {
        let results = await getAddressFromDaData(e.target.value)
        renderResults(results?.suggestions, 'REG')
    })

});