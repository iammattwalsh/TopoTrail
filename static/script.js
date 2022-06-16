// init materialize modals
// $(document).ready(function(){
//     $('.modal').modal();
// })

// materialize text entry char counter
$(document).ready(function() {
    $('input#id_name, textarea#id_desc').characterCounter();
})

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
        this.isThisATrail()
        this.getCurrentTrail()
        this.getTrailAssets(this.thisTrail)
    },
    mounted () {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]')
        this.csrf_token = input.value
        this.getUserTrails()
        this.initModalTest()
    },
    updated () {
        // this.initModalTest()
    },
    methods: {
        initModalTest () {
            var modals = document.querySelectorAll('.modal')
            modals.forEach(modal => {
                // modalid = modal.getAttribute('id')
                // modalid = '#' + modalid
                $('.modal').modal();
            })
        },
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
                    this.trailPhotos.forEach((eachPhoto, i) => {
                        eachPhoto.photoHREF = `#photo${eachPhoto.id}`
                        eachPhoto.photoID = `photo${eachPhoto.id}`
                    })
                    this.trailAssets = res.data.trail
                    // $(document).ready(function(){
                    //     $('.modal').modal();
                    // })
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
        selectNewTrailPhotos () {
            console.log('selectNewTrailPhotos start')
            Array.from(this.$refs.trailphotofile.files).forEach(file => {
                this.uploadNewTrailPhotos(file)

                this.newPhotos.push({
                    'name': file.name,
                    'status': 'is uploading',
                })
            })
            console.log('selectNewTrailPhotos end')
        },
        uploadNewTrailPhotos (file) {
            console.log('uploadNewTrailPhoto start')

            this.addNewTrailPhotos(file)
            .then(res => {
                this.newPhotos.forEach(newPhoto => {
                    if (newPhoto.name === file.name) {
                        newPhoto['status'] = 'is uploaded'
                    }
                })
                this.getTrailAssets()
            })
            .catch(error => {
                console.log(error)
                this.newPhotos.forEach(newPhoto => {
                    if (newPhoto.name === file.name) {
                        newPhoto['status'] = 'failed'
                    }
                })
            })
            console.log('uploadNewTrailPhoto start')
        },
        addNewTrailPhotos (file) {
            console.log('addNewTrailPhotos start')
            let formData = new FormData()
            formData.append('photo', file)

            return axios
                .post(`/trail/${this.thisTrail}/add_trail_photos`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'X-CSRFToken': this.csrf_token,
                    }
                })
        },
        // addTrailPhotos () {
        //     console.log(this.newPhotos)
        //     // this.newPhotos = []
        //     axios({
        //         method: 'post',
        //         url: `/trail/${this.thisTrail}/add_trail_photos`,
        //         data: {
        //             photos: this.newPhotos
        //         },
        //         headers: {
        //             'Content-Type': 'multipart/form-data',
        //             'X-CSRFToken': this.csrf_token,
        //         }
        //     }).then(res => {
        //         console.log(res)
        //         this.afterTrailPhotoUpload
        //     })
        // },
        // afterTrailPhotoUpload () {
        //     console.log('we made it to .then')
        // },
        // savePhotoCaptions () {

        // },
        testToggle () {
            this.trailAssets.texture_trail = '/uploads/mt-hood/texture_trail.png'
            this.trailAssets.mesh = '/uploads/mt-hood/mesh.obj'
        },
    },
}).mount('#app')