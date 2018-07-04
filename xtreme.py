#!/usr/bin/env python2

import os
import pygtk
import gtk
import pango
import gtk.glade
import database

class Xtreme:

    def __init__(self):
        '''Initialize Xtreme class'''
        self.database = database.Database()
        self.wTree = gtk.glade.XML('xtreme.glade','main_window')
        self.window = self.wTree.get_widget("main_window")
        self.window.connect("destroy", gtk.main_quit)
        dic = { 'on_quit' : self.on_quit,
            'on_edit' : self.on_edit,
            'on_cancel' : self.on_cancel,
            'on_save' : self.on_save,
            'on_new' : self.on_new,
            'on_deactivate' : self.on_deactivate,
            'on_reactivate' : self.on_reactivate,
            'on_execute' : self.on_execute,
            'on_reverse' : self.on_reverse,
            'on_about': self.on_about,
            'on_transaction' : self.on_transaction,
            'on_customer_changed' : self.on_customer_changed,
            'on_criteria_changed' : self.on_criteria_changed }
        self.wTree.signal_autoconnect(dic)
        self.configure_treeview()
        self.wTree.get_widget('criteria_combobox').set_active(0)
        self.load_customer_list()
        self.edit_mode(False)
        self.window.show()
        self.new_customer = False
        gtk.main()

    def configure_treeview(self):
        '''Configure the customers treeview'''
        self.wTree.get_widget('customerstreeview').get_selection().set_mode(gtk.SELECTION_SINGLE)
        store = gtk.ListStore(int, str, str, str, str, str, int, float, float, str, str)
        view = self.wTree.get_widget("customerstreeview")
        view.set_model(store)
        column_id = gtk.TreeViewColumn('ID')
        column_last = gtk.TreeViewColumn('Last Name')
        column_first = gtk.TreeViewColumn('First Name')
        column_monthly = gtk.TreeViewColumn('Monthly')
        column_owing = gtk.TreeViewColumn('Owing')
        column_membership = gtk.TreeViewColumn('Membership')
        view.append_column(column_last)
        view.append_column(column_first)
        view.append_column(column_monthly)
        view.append_column(column_owing)
        view.append_column(column_membership)
        cell_last = gtk.CellRendererText()
        cell_first = gtk.CellRendererText()
        cell_monthly = gtk.CellRendererText()
        cell_owing = gtk.CellRendererText()
        cell_membership = gtk.CellRendererText()
        column_last.pack_start(cell_last)
        column_first.pack_start(cell_first)
        column_monthly.pack_start(cell_monthly)
        column_owing.pack_start(cell_owing)
        column_membership.pack_start(cell_membership)
        column_last.add_attribute(cell_last,'text',2)
        column_first.add_attribute(cell_first,'text',1)
        column_monthly.set_cell_data_func(cell_monthly,self.cell_monthly_func)
        column_owing.set_cell_data_func(cell_owing,self.cell_owing_func)
        column_membership.set_cell_data_func(cell_membership,self.cell_membership_func)
        view.set_search_column(2)

    def cell_membership_func(self,column,cell,model,iter):
        '''Custom cell renderer for the membership column'''
        value = model.get_value(iter,6)
        if value == 0:
            cell.set_property('text', 'Open')
        elif value == 1:
            cell.set_property('text', 'Kickboxing')
        elif value == 2:
            cell.set_property('text', 'MMA')
        else:
            cell.set_property('text', 'Full')
        return

    def cell_monthly_func(self,column,cell,model,iter):
        '''Custom cell renderer for the monthly column'''
        value = '%1.2f' % model.get_value(iter,7)
        cell.set_property('text', value)
        return

    def cell_owing_func(self,column,cell,model,iter):
        '''Custom cell renderer for the owing column'''
        value = '%1.2f' % model.get_value(iter,8)
        cell.set_property('text',value)
        return

    def clear_fields(self):
        self.wTree.get_widget('firstentry').set_text('')
        self.wTree.get_widget('lastentry').set_text('')
        self.wTree.get_widget('phoneentry').set_text('')
        self.wTree.get_widget('emailentry').set_text('')
        self.wTree.get_widget('addresstextview').set_buffer(gtk.TextBuffer())
        self.wTree.get_widget('membershipcombobox').set_active(0)
        self.wTree.get_widget('monthlyentry').set_text('35.00')
        self.wTree.get_widget('owingentry').set_text('0.00')
        self.wTree.get_widget('commentstextview').set_buffer(gtk.TextBuffer())
        self.wTree.get_widget('transactions_textview').set_buffer(gtk.TextBuffer())
    
    def dialog_about(self):
        '''Create and show the about dialog'''
        dialog = gtk.AboutDialog()
        dialog.set_name('Xtreme Customer Database')
        dialog.set_version('0.1')
        dialog.set_authors(['Andrew Stephens'])
        dialog.set_transient_for(self.window)
        dialog.run()
        dialog.destroy()

    def dialog_message(self, title, message_format, type=gtk.MESSAGE_INFO):
        '''Create a message dialog'''
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        if type == gtk.MESSAGE_QUESTION:
            buttons = gtk.BUTTONS_YES_NO
        else:
            buttons = gtk.BUTTONS_OK
        dialog = gtk.MessageDialog(self.window, flags, type, buttons, message_format)
        dialog.set_transient_for(self.window)
        result = dialog.run()
        dialog.destroy()
        return result

    def dialog_transaction(self):
        '''Create and run transaction dialog'''
        (path,column) = self.wTree.get_widget('customerstreeview').get_cursor()
        wTree = gtk.glade.XML('xtreme.glade','transaction_dialog')
        dialog = wTree.get_widget('transaction_dialog')
        dialog.set_transient_for(self.window)
        wTree.get_widget('type_combobox').set_active(0)
        wTree.get_widget('type_combobox').grab_focus()
        result = dialog.run()
        if result == gtk.RESPONSE_ACCEPT:
            id = int(self.get_selected_id())
            type = wTree.get_widget('type_combobox').get_active()
            description = wTree.get_widget('description_entry').get_text()  
            amount = wTree.get_widget('amount_entry').get_text()
            if self.is_float(amount):
                amount = float(amount)
                if type == 0:
                    amount *= -1
                self.database.transaction(id,description,amount)
                self.load_customer_list()
                self.load_customer(id)
                self.dialog_message("Transaction Entered", "Transaction has been added")
            else:
                self.dialog_message("Input not valid", "Please use a number (currency) in the 'Amount' field.", gtk.MESSAGE_ERROR)
                self.dialog_transaction()
        dialog.destroy()
        self.wTree.get_widget('customerstreeview').set_cursor(path)

    def edit_mode(self, edit):
        '''Set the edit mode to true or false'''
        self.wTree.get_widget('customerstreeview').set_sensitive(not edit)
        self.wTree.get_widget('firstentry').set_sensitive(edit)
        self.wTree.get_widget('lastentry').set_sensitive(edit)
        self.wTree.get_widget('phoneentry').set_sensitive(edit)
        self.wTree.get_widget('emailentry').set_sensitive(edit)
        self.wTree.get_widget('addresstextview').set_sensitive(edit)
        self.wTree.get_widget('membershipcombobox').set_sensitive(edit)
        self.wTree.get_widget('monthlyentry').set_sensitive(edit)
        self.wTree.get_widget('owingentry').set_sensitive(edit)
        self.wTree.get_widget('commentstextview').set_sensitive(edit)
        self.wTree.get_widget('new_button').set_sensitive(not edit)
        self.wTree.get_widget('edit_button').set_sensitive(not edit)
        self.wTree.get_widget('transaction_button').set_sensitive(not edit)
        self.wTree.get_widget('cancel_button').set_sensitive(edit)
        self.wTree.get_widget('save_button').set_sensitive(edit)
        if edit:
            self.wTree.get_widget('firstentry').grab_focus()
        else:
            self.wTree.get_widget('customerstreeview').grab_focus()

    def get_selected_id(self):
        '''Return selected id from customer list or None'''
        (model,iter) = self.wTree.get_widget('customerstreeview').get_selection().get_selected()
        if iter:
            id = model.get_value(iter,0)
            return int(id)
        else:
            return None

    def get_selected_field(self, index):
        '''Return the value of the field number for the selected row'''
        (model,iter) = self.wTree.get_widget('customerstreeview').get_selection().get_selected()
        if iter:
            return model.get_value(iter,index)
        else:
            return None

    def is_float(self, variable):
        '''Is variable a floating point number'''
        try:
            float(variable)
            return True
        except ValueError:
            return False

    def load_customer(self, id):
        '''Load customer from database into edit area'''
        customer = self.database.get_customer(id)
        self.wTree.get_widget('firstentry').set_text(customer[1])
        self.wTree.get_widget('lastentry').set_text(customer[2])
        self.wTree.get_widget('phoneentry').set_text(customer[3])
        self.wTree.get_widget('emailentry').set_text(customer[4])
        addressbuffer = gtk.TextBuffer()
        addressbuffer.set_text(customer[5])
        self.wTree.get_widget('addresstextview').set_buffer(addressbuffer)
        try:
            membership_index = int(customer[6])
        except ValueError:
            membership_index = 0
        self.wTree.get_widget('membershipcombobox').set_active(membership_index)
        self.wTree.get_widget('monthlyentry').set_text( str(customer[7]) )
        self.wTree.get_widget('owingentry').set_text( str(customer[8]) )
        commentsbuffer = gtk.TextBuffer()
        commentsbuffer.set_text(customer[9])
        self.wTree.get_widget('commentstextview').set_buffer(commentsbuffer)
        text = ''
        for transaction in self.database.get_transactions(customer_id=id):
            text += '%-20s  %-40s   %1.2f\n' % (transaction[0],transaction[1][:40],transaction[2])
        transactions_buffer = gtk.TextBuffer()
        transactions_buffer.set_text(text)
        self.wTree.get_widget('transactions_textview').set_buffer(transactions_buffer)
        self.wTree.get_widget('transactions_textview').modify_font(pango.FontDescription('Courier 10'))

    def load_customer_list(self):
        '''Load customers from database into the treeview'''
        treeview = self.wTree.get_widget('customerstreeview')
        store = treeview.get_model()
        store.clear()
        criteria = self.wTree.get_widget('criteria_combobox').get_active()
        if criteria == 0:
            customers = self.database.get_customers()
        elif criteria == 1:
            customers = self.database.get_customers(owing=True)
        elif criteria == 2:
            customers = self.database.get_customers(membership=0)
        elif criteria == 3:
            customers = self.database.get_customers(membership=1)
        elif criteria == 4:
            customers = self.database.get_customers(membership=2)
        elif criteria == 5:
            customers = self.database.get_customers(membership=3)
        elif criteria == 6:
            customers = self.database.get_customers(active=False)
        else:
            customers = []
        for customer in customers:
            try:
                store.append(customer[:-1])
            except:
                print len(customer)
        treeview.queue_draw()
        self.wTree.get_widget('display_label').set_text('Displaying %d Customers' % len(customers))

    def on_about(self, widget):
        '''About event handler'''
        self.dialog_about()
    
    def on_cancel(self, widget):
        '''Cancel event handler'''
        self.new_customer = False
        id = self.get_selected_id()
        if id:
            self.load_customer(id)
        else:
            self.clear_fields()
        self.edit_mode(False)

    def on_criteria_changed(self, widget):
        '''Criteria changed event handler'''
        self.load_customer_list()
        self.on_customer_changed(None)

    def on_customer_changed(self, widget):
        '''Customer selection changed handler'''
        customer_id = self.get_selected_field(0)
        active = self.get_selected_field(10)
        if customer_id:
            status = True
            self.load_customer(customer_id)
        else:
            status = False
            self.clear_fields()
        self.wTree.get_widget('edit_menuitem').set_sensitive(status)
        self.wTree.get_widget('edit_button').set_sensitive(status)
        self.wTree.get_widget('transaction_menuitem').set_sensitive(status)
        self.wTree.get_widget('transaction_button').set_sensitive(status)
        self.wTree.get_widget('deactivate_menuitem').set_sensitive(False)
        self.wTree.get_widget('reactivate_customer_menuitem').set_sensitive(False)
        if customer_id and str(active) == 'true':
            self.wTree.get_widget('deactivate_menuitem').set_sensitive(True)
        elif customer_id and str(active) == 'false':
            self.wTree.get_widget('reactivate_customer_menuitem').set_sensitive(True)

    def on_deactivate(self, widget):
        '''Deactivate event handler'''
        id = self.get_selected_id()
        if self.dialog_message('Deactivate Customer?','Are you sure you want to deactivate this customer?',gtk.MESSAGE_QUESTION) == gtk.RESPONSE_YES:
            self.database.save_customer_active(customer_id=id,active='false')
            self.load_customer_list()   
            self.dialog_message('Customer Deactivated','Customer has been deactivated.')

    def on_edit(self, widget):
        '''Edit event handler'''
        self.edit_mode(True)

    def on_execute(self, widget, reverse=False):
        '''Execute payday event handler'''
        if reverse:
            title = 'Reverse Payday?'
            message = 'Are you sure you want to reverse the last payday?\n(This is only necessary if an extra payday was added accidentally)'
        else:
            title = 'Payday?'
            message = 'Are you sure you want to make today a payday?'
        if self.dialog_message(title,message,gtk.MESSAGE_QUESTION) == gtk.RESPONSE_YES:
            watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
            self.window.window.set_cursor(watch)
            self.window.set_sensitive(False)
            self.database.payday_execute(reverse)
            self.load_customer_list()
            self.window.set_sensitive(True)
            if reverse:
                title = 'Payday Reversed'
                message = 'The last payday has been reversed.'
            else:
                title = 'Payday Complete'
                message = 'A payday has been created.\nAll customers have had their monthly fees added.'
            self.dialog_message(title,message)
            self.window.window.set_cursor(None)

    def on_new(self, widget):
        '''New event handler'''
        self.new_customer = True
        self.clear_fields()
        self.edit_mode(True)

    def on_quit(self, widget):
        '''Quit event handler'''
        gtk.main_quit()

    def on_reactivate(self, widget):
        '''Reactivate event handler'''
        customer_id = self.get_selected_id()
        self.database.save_customer_active( customer_id=customer_id, active='true' )
        self.load_customer_list()
        self.dialog_message( 'Customer Reactivated', 'Customer has been reactivated.' )

    def on_reverse(self, widget):
        '''Reverse payday event handler'''
        self.on_execute(widget=None,reverse=True)

    def on_save(self, widget):
        '''Save event handler'''
        firstname = self.wTree.get_widget('firstentry').get_text().rstrip().lstrip()
        lastname = self.wTree.get_widget('lastentry').get_text().rstrip().lstrip()
        phone = self.wTree.get_widget('phoneentry').get_text().rstrip().lstrip()
        email = self.wTree.get_widget('emailentry').get_text().rstrip().lstrip()
        addressbuffer = self.wTree.get_widget('addresstextview').get_buffer()
        address = addressbuffer.get_text(addressbuffer.get_start_iter(),addressbuffer.get_end_iter()).rstrip().lstrip()
        membership = str(self.wTree.get_widget('membershipcombobox').get_active()).rstrip().lstrip()
        monthly = self.wTree.get_widget('monthlyentry').get_text()
        commentsbuffer = self.wTree.get_widget('commentstextview').get_buffer()
        comments = commentsbuffer.get_text(commentsbuffer.get_start_iter(),commentsbuffer.get_end_iter()).rstrip().lstrip()
        if len(firstname) == 0:
            self.wTree.get_widget('firstentry').grab_focus()
        elif len(lastname) == 0:
            self.wTree.get_widget('lastentry').grab_focus()
        elif self.is_float(monthly) == False:
            self.wTree.get_widget('monthlyentry').grab_focus()
        else:
            (path,column) = self.wTree.get_widget('customerstreeview').get_cursor()
            if self.new_customer:
                customer_id = self.database.new_customer(firstname,lastname,phone,email,address,membership,monthly,comments)
            else:
                customer_id = self.get_selected_id()
                self.database.save_customer(customer_id,firstname,lastname,phone,email,address,membership,monthly,comments)
            self.edit_mode(False)
            self.load_customer_list()
            self.dialog_message('Customer Saved', 'Customer information has been saved.')
            self.new_customer = False
            self.wTree.get_widget('customerstreeview').set_cursor(path)


    def on_transaction(self, widget):
        '''Transaction event handler'''
        self.dialog_transaction()

if __name__ == '__main__':
    Xtreme()
