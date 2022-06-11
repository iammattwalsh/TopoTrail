// init materialize modals
$(document).ready(function(){
    $('.modal').modal();
})

$(document).ready(function() {
    $('input#id_name, textarea#id_desc').characterCounter();
});

Vue.createApp({
    data () {
        return {
            blah:'blah',
            isHidden: {
                loginRegister: true,
                newTrail: true,
            },
        }
    },
    delimiters: ['[[', ']]'],
    created () {
        // this.testTheThing()
        
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
        loadPage () {
            axios ({
                method: 'get',
                url: '/test/test-trail-1'
            }).then(res => {
                console.log('boop')
                console.log(res.data)
            })
        },
    },
}).mount('#app')