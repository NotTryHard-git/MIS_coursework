<script>
import AdminCatalog from '@/components/AdminCatalog.vue';
import AdminNavPanel from '@/components/AdminNavPanel.vue';
import Footer from '@/components/Footer.vue';
import Header from '@/components/Header.vue';

export default {
    components:{
        AdminNavPanel,
        AdminCatalog,
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
   <AdminCatalog></AdminCatalog>
    <Footer></Footer>
</template>
<style scoped>
</style>
