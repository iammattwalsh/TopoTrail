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

const app = Vue.createApp({
    data () {
        return {
            csrf_token: '',
            isTrail: false,
            thisTrail: null,
            trailPhotos: [],
            trailAssets: {},
            userTrails: [],
            newPhotos: [],
        }
    },
    delimiters: ['[[', ']]'],
    created () {
        // this.testTheThing()
        this.isThisATrail(),
        this.getCurrentTrail(),
        this.getTrailAssets(this.thisTrail)
    },
    mounted () {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]')
        this.csrf_token = input.value
        this.getUserTrails()
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
        getTrailAssets () {
            if (this.isTrail) {
                axios ({
                    method: 'get',
                    url: `/trail/${this.thisTrail}/get_trail_assets`
                }).then(res => {
                    // console.log(res.data.photos)
                    this.trailPhotos = res.data.photos
                    this.trailPhotos.forEach(eachPhoto => {
                        eachPhoto.photoHREF = `#photo${eachPhoto.id}`
                        eachPhoto.photoID = `photo${eachPhoto.id}`
                    })
                    this.trailAssets = res.data.trail
                })
            }
        },
        getUserTrails () {
            if (this.isTrail) {
                axios ({
                    method: 'get',
                    url: `/trail/${this.thisTrail}/get_user_trails`
                }).then(res => {
                    this.userTrails = res.data.user_trails
                })
            }
        },
        addTrailPhotos () {
            // this.newPhotos = []
            axios({
                method: 'post',
                url: `/trail/${this.thisTrail}/add_trail_photos`,
                data: {
                    photos: this.newPhotos
                },
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': this.csrf_token,
                }
            }).then(res => {
                console.log(res)
                this.afterTrailPhotoUpload
            })
        },
        afterTrailPhotoUpload () {
            console.log('we made it to .then')
        },
        savePhotoCaptions () {

        },
        testToggle () {
            this.trailAssets.texture_trail = '/uploads/mt-hood/texture_trail.png'
            this.trailAssets.mesh = '/uploads/mt-hood/mesh.obj'
        },
    },
}).mount('#app')