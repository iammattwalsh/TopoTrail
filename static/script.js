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
            currentTrail: '',
        }
    },
    delimiters: ['[[', ']]'],
    created () {
        // this.testTheThing()
        this.getCurrentTrail()
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
        getCurrentTrail () {
            // this.location = window.location.href.toString().split(window.location.host + '/trail/')[1]
            // if (this.location[-1] == '#') {
            //     this.location = this.location[]
            // }
            // console.log(this.location)
        },
        getTrailPhotos () {
            const trail = this.$refs.trail_slug_anchor.innerText
            console.log(trail)
            axios ({
                method: 'get',
                url: `/trail/${trail}/get_trail_photos`
            }).then(res => {
                console.log(res)
            })
        },
    },
}).mount('#app')