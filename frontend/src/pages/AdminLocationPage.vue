<script>
import AdminLocation from '@/components/AdminLocation.vue';
import AdminNavPanel from '@/components/AdminNavPanel.vue';
import Footer from '@/components/Footer.vue';
import Header from '@/components/Header.vue';

export default {
    components:{
        AdminNavPanel,
        AdminLocation,
        Header,
        Footer
    },
  data(){
    return{
      state1: 0
    }
  }
}
</script>
<template>
   <Header></Header>
   <AdminNavPanel></AdminNavPanel>
   <AdminLocation></AdminLocation>
    <Footer></Footer>
</template>
<style scoped>
</style>
