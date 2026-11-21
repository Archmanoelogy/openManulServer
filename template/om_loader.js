function nav_toggle(sender){
    sender.classList.toggle('active')
}
function nav_selectAll(sender, event){
    event.preventDefault();
    event.stopPropagation();
    const details = sender.closest('details');
    const items = details.querySelectorAll('li a');
    for(const a of items){
        a.classList.add('active');
    }
}
function nav_deselectAll(sender, event){
    event.preventDefault();
    event.stopPropagation();
    const details = sender.closest('details');
    const items = details.querySelectorAll('li a');
    for(const a of items){
        a.classList.remove('active');
    }
}

document.addEventListener('click', function(event){
    const options = document.querySelectorAll('header nav li.nav-dropdown details[open]');
	for(const opt of options){
        if (!opt.contains(event.target)) {
            opt.removeAttribute('open');
        }
    }
	const references = document.querySelectorAll('omr');
	for(omr of references){
        if (omr.contains(event.target)) {
            const ref_id   = omr.innerHTML;
			const manul_id = omr.closest('a.bm').name;
			window.location.href = `/reference/manul/${manul_id}/${ref_id}`;
        }
    }
});
