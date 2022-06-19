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
            trailThumbsWidth: 0,
            numThumb: 2,
            showThumb: [],
            newComment: '',
            trailComments: [],
            editedDesc: '',
            trailDescEdit: true,
            editedShare: '',
            shareOptions: {
                'private':'Private',
                'public':'Public',
                'link':'Share with link'
            }

        }
    },
    delimiters: ['[[', ']]'],
    created () {
        this.isThisATrail()
        this.getCurrentTrail()
        this.getTrailAssets()
    },
    mounted () {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]')
        this.csrf_token = input.value
        this.getUserTrails()
        this.initModals()
        this.initAddPhotoModal()
        this.initMaterializeComps()
        this.initMaterializeCharCount()
        this.$nextTick(() => {
            setTimeout(() => {
                this.getDimensions()
            },100)
        })
        window.addEventListener('resize', this.getDimensions)
    },
    updated () {
        this.initModals()
    },
    methods: {
        getDimensions () {
            // windowWidth = window.innerWidth
            // asideWidth = document.getElementById('aside').clientWidth
            // console.log(`window ${windowWidth}`)
            // console.log(`aside ${asideWidth}`)
            // this.trailThumbsWidth = windowWidth - asideWidth
            if (this.trailThumbsWidth == 0) {
                this.trailThumbsWidth = document.getElementById('trail-photos').clientWidth - 20
            } else {
                this.trailThumbsWidth = document.getElementById('trail-photos').clientWidth
            }
            this.numTrailThumbs()
        },
        numTrailThumbs () {
            this.numThumb = Math.floor(this.trailThumbsWidth / 150)
            this.showThumb = this.trailPhotos.slice(`-${this.numThumb}`,)
        },
        initModals () {
            var modals = document.querySelectorAll('.modal:not(#modal-add-photos')
            console.log(modals)
            modals.forEach(modal => {
                $(modal).modal();
            })
        },
        initAddPhotoModal () {
            $('#modal-add-photos').modal({
                onCloseEnd: _ => {
                    this.getTrailAssets()
                }
            })
        },
        initMaterializeCharCount () {
            // materialize text entry char counter
            $('input#id_name, textarea#id_desc, textarea#id_comment, textarea#edittraildesc').characterCounter();
        },
        initMaterializeComps () {
            // materialize collabsible
            $('.collapsible').collapsible({
                accordion: false
            });
            // materialize sidenav
            $('.sidenav').sidenav();
            // materialize form selectbox
            $('select').formSelect();
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
        },
        getTrailAssets () {
            if (this.isTrail) {
                axios ({
                    method: 'get',
                    url: `/trail/${this.thisTrail}/get_trail_assets`
                }).then(res => {
                    this.trailPhotos = res.data.photos
                    this.trailPhotos.forEach((eachPhoto, i) => {
                        eachPhoto.photoHREF = `#photo${eachPhoto.id}`
                        eachPhoto.photoID = `photo${eachPhoto.id}`
                    })
                    this.trailAssets = res.data.trail
                    this.trailComments = res.data.comment
                    this.numTrailThumbs()
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
            // console.log('selectNewTrailPhotos start')
            Array.from(this.$refs.trailphotofile.files).forEach(file => {
                this.uploadNewTrailPhotos(file)

                this.newPhotos.push({
                    'name': file.name,
                    'status': 'is uploading',
                })
            })
            // console.log('selectNewTrailPhotos end')
        },
        uploadNewTrailPhotos (file) {
            // console.log('uploadNewTrailPhoto start')
            this.addNewTrailPhotos(file)
            .then(res => {
                this.newPhotos.forEach(newPhoto => {
                    if (newPhoto.name === file.name) {
                        newPhoto['status'] = 'is uploaded'
                    }
                })
                // this.getTrailAssets()
            })
            .catch(error => {
                console.log(error)
                this.newPhotos.forEach(newPhoto => {
                    if (newPhoto.name === file.name) {
                        newPhoto['status'] = 'failed'
                    }
                })
            })
            // console.log('uploadNewTrailPhoto start')
        },
        addNewTrailPhotos (file) {
            // console.log('addNewTrailPhotos start')
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
        addTrailComment () {
            console.log('start add trail comment')
            let formData = new FormData()
            formData.append('comment',this.newComment)
            console.log('get form data')
            console.log(formData)
            return axios
                .post(`/trail/${this.thisTrail}/add_trail_comment`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'X-CSRFToken': this.csrf_token,
                    }
                })
                .then(
                    this.newComment = ''
                )
        },
        toggleTrailDescEdit () {
            if (this.trailDescEdit) {
                this.trailDescEdit = false
                this.editedDesc = this.trailAssets.desc
                this.$nextTick(() => {
                    setTimeout(() => {
                        this.initMaterializeCharCount()
                    },100)
                textArea = document.getElementById('edittraildesc')
                textArea.style.height = `${textArea.scrollHeight}px`
                })
            } else {
                this.trailDescEdit = true
                this.editedDesc = ''
            }
        },
        updateEditedShare () {
            select = document.getElementById('trailshareselect')
            this.editedShare = select.value
            console.log(select.value)
        },
        cancelEditTrail () {
            this.editedDesc = ''
            this.editedShare = ''
        },
        selectShareOption () {
            select = document.getElementById('trailshareselect')
            M.FormSelect.init(select)
        },
        editTrail () {
            let formData = new FormData()
            if (this.editedDesc) {
                formData.append('desc',this.editedDesc)
                this.trailAssets.desc = this.editedDesc
            }
            if (this.editedShare) {
                formData.append('share',this.editedShare)
                this.$nextTick(() => {
                    setTimeout(() => {
                        this.trailAssets.share = this.editedShare
                    },100)
                })
            }
            return axios
                .post(`/trail/${this.thisTrail}/edit`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'X-CSRFToken': this.csrf_token,
                    }
                })
        },
        testToggle () {
            this.trailAssets.texture_trail = '/uploads/mt-hood/texture_trail.png'
            this.trailAssets.mesh = '/uploads/mt-hood/mesh.obj'
        },
    },
}).mount('#app')