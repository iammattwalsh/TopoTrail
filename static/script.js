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
        
    },
    mounted () {

    },
    methods: {
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