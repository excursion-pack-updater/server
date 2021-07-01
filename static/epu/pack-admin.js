function setup()
{
    for(let div of document.querySelectorAll(".field-icon div"))
    {
        const select = div.querySelector("select");
        const img = document.createElement("img");
        img.width = 64;
        img.height = 64;
        
        div.insertBefore(img, select);
        select.addEventListener("change", changed);
        changed.bind(select)();
    }
}

document.addEventListener("DOMContentLoaded", setup);

function changed()
{
    const filename = this.value.match(/[^/]+.png$/)[0];
    const img = this.parentElement.querySelector("img");
    img.src = `/static/epu/icons/${filename}`;
}
