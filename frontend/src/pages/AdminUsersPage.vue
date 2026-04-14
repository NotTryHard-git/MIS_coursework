<script>
import AdminUsers from '@/components/AdminUsers.vue';
import AdminNavPanel from '@/components/AdminNavPanel.vue';
import Footer from '@/components/Footer.vue';
import Header from '@/components/Header.vue';

export default {
    components:{
        AdminNavPanel,
        AdminUsers,
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
   <AdminUsers></AdminUsers>
    <Footer></Footer>
</template>
<style scoped>
</style>
