// init materialize modals
$(document).ready(function(){
    $('.modal').modal();
})

// materialize text entry char counter
$(document).ready(function() {
    $('input#id_name, textarea#id_desc').characterCounter();
});

// materialize media lightbox
$(document).ready(function(){
    $('.materialboxed').materialbox();
});

Vue.createApp({
    data () {
        return {
            blah:'blah',
            isTrail: false,
            thisTrail: null,
            trailPhotos: [],
        }
    },
    delimiters: ['[[', ']]'],
    created () {
        // this.testTheThing()
        this.isThisATrail(),
        this.getCurrentTrail(),
        this.getTrailPhotos(this.thisTrail)
    },
    mounted () {
        
    },
    methods: {
        // testTheThing () {
        //     console.log('boop')
        // },
        // toggleHidden (element) {
        //     // toggle hidden/visible with key to isHidden object passed as string parameter
        //     if (this.isHidden[element]) {
        //         this.isHidden[element] = false
        //     } else {
        //         this.isHidden[element] = true
        //     }
        // },
        // loadPage () {
        //     axios ({
        //         method: 'get',
        //         url: '/test/test-trail-1'
        //     }).then(res => {
        //         console.log('boop')
        //         console.log(res.data)
        //     })
        // },
        isThisATrail () {
            // use URL to determine if current page is a trail
            const host = window.location.host
            const href = window.location.href.toString()
            splitURL = href.split(host).join('').split('/')
            this.isTrail = splitURL.includes('trail')
        },
        getCurrentTrail () {
            // use URL to determine which trail this is
            if (this.isTrail) {
                this.thisTrail = splitURL[splitURL.indexOf('trail')+1]
                if (this.thisTrail.includes('#')) {
                    this.thisTrail = this.thisTrail.slice(0,this.thisTrail.indexOf('#'))
                }
            }
            // FUTURE NOTE - a user could break this by including a "#" in their trail name (which hopefully they wouldn't do but you never know)
        },
        getTrailPhotos (trail) {
            if (this.isTrail) {
                axios ({
                    method: 'get',
                    url: `/trail/${trail}/get_trail_photos`
                }).then(res => {
                    console.log(res.data.photos)
                    this.trailPhotos = res.data.photos
                    this.trailPhotos.forEach(eachPhoto => {
                        eachPhoto.photoHREF = `#photo${eachPhoto.id}`
                        eachPhoto.photoID = `photo${eachPhoto.id}`
                        // eachPhoto.captionExt = `${eachPhoto.caption} &#13; Uploaded by ${eachPhoto.user} on ${new Date(eachPhoto.timestamp).toLocaleDateString()} at ${new Date(eachPhoto.timestamp).toLocaleTimeString()}.`
                    })
                })
            }
        },
        getPhotoURL (photoPath) {
            const host = window.location.host
            return `${host}/trail/${photoPath}`
        },
    },
}).mount('#app')