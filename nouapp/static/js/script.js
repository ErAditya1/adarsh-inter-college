window.addEventListener('scroll',()=>{
    
    if(window.scrollY > 100){
        document.querySelector('.back-to-top').classList.add('active')
    }else{
        document.querySelector('.back-to-top').classList.remove('active')
    }
})

function getSlidesPerView() {
    const screenWidth = window.innerWidth;

    if (screenWidth > 1024) {
        return 3; // Show 4 slides per view for large screens
    } else if (screenWidth > 768) {
        return 2; // Show 2 slides per view for medium screens
    } else {
        return 1; // Show 1 slide per view for small screens
    }
}

    document.addEventListener('DOMContentLoaded', function () {

        
        var swiper = new Swiper('.swiper', {
           
            slidesPerView: getSlidesPerView(),
            centeredSlides: true,
            spaceBetween: 30,
            direction: 'horizontal',
            loop: true,
            autoplay:{
                delay: 2500,
                disableOnInteraction: false,
            },

            // If you want pagination
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },

            // If you want navigation buttons
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },

            // And if you need scrollbar
            scrollbar: {
                el: '.swiper-scrollbar',
            },
        });
       
    });
    

    window.addEventListener('resize',()=>{
        console.log("window resized")
    })
    






const  sideMenu = document.querySelector('aside');
const menuBtn = document.querySelector('#menu_bar');
const closeBtn = document.querySelector('#close_btn');




const toggleButton = document.querySelector('.theme-controller')  
const body = document.querySelector('html');


// Optional: Check if user has dark mode preference set in OS
if (localStorage.getItem('theme')) {
    if(localStorage.getItem('theme') == 'dark' && !body.classList.contains('dark')) {
        console.log("containst dark")
        body.classList.add('dark');
        toggleButton.checked = false;
    }else{
        console.log("containst light")
        toggleButton.checked = true;
        body.classList.remove('dark');
    }

}else if( window.matchMedia('(prefers-color-scheme: dark)').matches && !body.classList.contains('dark')){

    body.classList.add('dark');
    document.cookie = "dark_mode=true;";
}
else if( !window.matchMedia('(prefers-color-scheme: dark)').matches && body.classList.contains('dark')){
    
    body.classList.add('dark');
    document.cookie = "dark_mode=true;";
}



toggleButton.addEventListener('click', () => {
    if (body.classList.contains('dark')) {
        body.classList.remove('dark');
        localStorage.setItem('theme', 'light')
    } else {
        body.classList.add('dark');
        localStorage.setItem('theme', 'dark')
        document.cookie = "dark_mode=true; ";
    }
});





themeToggler.addEventListener('click',()=>{
     document.body.classList.toggle('dark-theme-variables')
     themeToggler.querySelector('span:nth-child(1').classList.toggle('active')
     themeToggler.querySelector('span:nth-child(2').classList.toggle('active')
})


window.addEventListener('DOMContentLoaded',()=>{
    console.log("DOM fully loaded and parsed")
    active_link.style.color = "red"
})

window.addEventListener('load',()=>{
    console.log("page fully loaded")
})

window.addEventListener('resize',()=>{
    console.log("window resized")
})

window.addEventListener('beforeunload',()=>{
    console.log("page about to be unloaded")
})

window.addEventListener('keydown',(e)=>{
    console.log("key pressed", e.key)
})

const back_to_top = document.querySelector('back-to-top')
window.addEventListener('scroll',()=>{
    if(back_to_top){

    
    if(window.scrollY > 100){
        back_to_top.classList.add('active')
    }else{
        back_to_top.classList.remove('active')
    }
}
})