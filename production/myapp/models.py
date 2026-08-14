from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError


def format_float(value):
    """Format float to remove .0 for whole numbers and limit to 2 decimals"""
    if value is None:
        return ""
    if value == int(value):
        return str(int(value))
    else:
        # Truncate to 2 decimal places without rounding
        truncated = int(value * 100) / 100.0
        return f"{truncated:.2f}"


# ================= USER =================
class CustomUser(AbstractUser):
    
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Operator', 'Operator'),   
        ('operator_manager', 'operator_manager'),
        ('Operator_incharge', 'Operator_incharge'),
        ('Manager', 'Manager'),
        ('Dispatch', 'Dispatch'),
        ('Batcher', 'Batcher'),
        ('Dispatch Manager', 'Dispatch Manager'),
    )
    full_name = models.CharField(max_length=200)
    contact = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField()

    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f'{self.user.username} - {self.date}'

# ================= MASTER TABLES =================
class Color(models.Model):
    color = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.color.upper()


class Thickness(models.Model):
    thickness = models.FloatField(unique=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.thickness is not None and self.thickness > 36:
            raise ValidationError("Invalid number. Thickness cannot be greater than 36.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return format_float(self.thickness)


class Density(models.Model):
    density = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.density)   
    
class DensityName(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Party(models.Model):
    c_name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=500)
    gst = models.CharField(max_length=50)
    state = models.CharField(max_length=100)
    psft = models.CharField(max_length=2)  # Price per square feet (2-digit varchar)

    def __str__(self):
        return self.c_name


class Size(models.Model):
    size = models.CharField(max_length=50, unique=True)
    standard_weight = models.FloatField(null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.size


class Length(models.Model):
    UNIT_CHOICES = (
        ('ft', 'Feet'),
        ('mm', 'MM'),
    )

    length = models.FloatField(unique=True)  # ALWAYS stored in FEET
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='ft')
    original_value = models.FloatField(null=True, blank=True)  # what user entered

    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.unit == "mm":
            return f"{format_float(self.original_value)} mm"
        return f"{format_float(self.original_value)} ft"


class Width(models.Model):
    UNIT_CHOICES = (
        ('inch', 'Inch'),
        ('mm', 'MM'),
    )

    width = models.FloatField(unique=True)  # ALWAYS stored in INCHES
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='inch')
    original_value = models.FloatField(null=True, blank=True)  # what user entered

    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.width is not None and self.width > 49:
            raise ValidationError("Invalid number. Width cannot be greater than 49 inches.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.unit == "mm":
            return f"{format_float(self.original_value)} mm"
        return f"{format_float(self.original_value)} inch"


class Height(models.Model):
    UNIT_CHOICES = (
        ('inch', 'Inch'),
        ('mm', 'MM'),
    )

    height = models.FloatField(unique=True)  # ALWAYS stored in INCHES
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='inch')
    original_value = models.FloatField(null=True, blank=True)  # what user entered

    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.height is not None and self.height < 48:
            raise ValidationError("Invalid number. Height cannot be less than 48 inches.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.unit == "mm":
            return f"{format_float(self.original_value)}"
        return f"{format_float(self.original_value)}"


# ================= PRODUCT =================
class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Door', 'Door'),
        ('Frame', 'Frame'),
        ('Sheet', 'Sheet')
    )

    STAMP_CHOICES = (
        ("Star", "Star"),
        ("Royal", "Royal"),
        ("Gold", "Gold"),
        ("Diamonds", "Diamonds"),
        ("Platinum", "Platinum"),
        ("Premium", "Premium")
    )

    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)

    # attributes
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.PROTECT)
    thickness = models.ForeignKey(Thickness, null=True, blank=True, on_delete=models.PROTECT)
    density = models.ForeignKey(Density, null=True, blank=True, on_delete=models.PROTECT)
    density_name = models.ForeignKey(DensityName,on_delete=models.PROTECT,null=True,blank=True)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.PROTECT)
    length = models.ForeignKey(Length, null=True, blank=True, on_delete=models.PROTECT)
    width = models.ForeignKey(Width, null=True, blank=True, on_delete=models.PROTECT)
    height = models.ForeignKey(Height, null=True, blank=True, on_delete=models.PROTECT)
    stamp = models.CharField(max_length=20, choices=STAMP_CHOICES, blank=True, default="")

    #  AUTO NAME GENERATION
    def generate_name(self):
        if self.category == "Frame":
            return f"WPC Frame {self.size} -{self.length} {self.color}"

        elif self.category in ["Door", "Sheet"]:
            # Use raw values instead of __str__() to avoid units and uppercasing
            h = format_float(self.height.height) if self.height else ""
            w = format_float(self.width.width) if self.width else ""
            c = self.color.color if self.color else ""
            stamp_str = f" {self.stamp}" if self.stamp else ""
            return f"WPC Door {self.thickness}mm {w}x{h}{stamp_str} {c}"


        return "Unknown Product"

    def save(self, *args, **kwargs):    
       
        # Auto name
        self.product_name = self.generate_name()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            'category', 'color', 'thickness', 'density',
            'size', 'length', 'width', 'height', 'stamp'
        )

    def __str__(self):
        return self.product_name


# ================= MACHINE =================
class Machine(models.Model):
    CATEGORY_CHOICES = (
        ('Door', 'Door'),
        ('Frame', 'Frame'),
        ('Sheet', 'Sheet')
    )
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ================= MACHINE OPERATOR LINK =================
class MachineOperator(models.Model):
    CATEGORY_CHOICES = (
        ('Door', 'Door'),
        ('Frame', 'Frame'),
        ('Sheet', 'Sheet')
    )
    
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='machine_categories')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    class Meta:
        unique_together = ('operator', 'category')

    def __str__(self):
        return f"{self.operator.username} - {self.category} Machines"


# ================= PRODUCTION =================
class Production(models.Model):
    SHIFT_CHOICES = (
        ('Day', 'Day'),
        ('Night', 'Night'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    PATTAM_CHOICES = (
        ('S.P.', 'Single Pattam'),
        ('D.P.', 'Double Pattam'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    #  IMPORTANT: REMOVE dependency on product
    category = models.CharField(max_length=10, choices=Product.CATEGORY_CHOICES)

    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.PROTECT)
    thickness = models.ForeignKey(Thickness, null=True, blank=True, on_delete=models.PROTECT)
    density = models.ForeignKey(Density, null=True, blank=True, on_delete=models.PROTECT)
    density_name = models.ForeignKey(DensityName, null=True, blank=True, on_delete=models.PROTECT)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.PROTECT)
    length = models.ForeignKey(Length, null=True, blank=True, on_delete=models.PROTECT)
    width = models.ForeignKey(Width, null=True, blank=True, on_delete=models.PROTECT)
    height = models.ForeignKey(Height, null=True, blank=True, on_delete=models.PROTECT)

    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    quantity = models.IntegerField()
    weight_per_piece = models.FloatField()

    sidepatti = models.FloatField(default=0)
    linesetting = models.FloatField(default=0)

    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    remark = models.CharField(max_length=200,blank=True)

    # Rejection tracking
    rejection_status = models.CharField(max_length=20, choices=[('OK', 'OK'), ('Unfinished', 'Unfinished'), ('Scrap', 'Scrap')], default='OK')
    rejected_quantity = models.FloatField(default=0)

    created_at = models.DateTimeField(default=timezone.now)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    edited = models.BooleanField(default=False)

    weight_sheet = models.OneToOneField('WeightSheet',null=True,blank=True,on_delete=models.SET_NULL,related_name='production')
    
    # Hidden connection to Planning (internal only, not visible to website users)
    planning = models.ForeignKey('Planning', null=True, blank=True, on_delete=models.SET_NULL, editable=False)

    
    def __str__(self):
        return f"{self.category} - {self.quantity} ({self.status})"

    @property
    def total_weight(self):
        return self.quantity * self.weight_per_piece

    @property
    def standard_weight(self):
        return self.size.standard_weight if self.size and self.size.standard_weight is not None else 0

    @property
    def total_norm_weight(self):
        length_val = self.length.length if self.length and self.length.length is not None else 0
        weight = self.quantity * length_val * self.standard_weight
        return round(weight, 2)

    @property
    def excess(self):
        return self.total_weight - self.total_norm_weight

    @property
    def actual_production(self):
        return self.total_weight

    @property
    def total_scrap(self):
        return self.sidepatti + self.linesetting

    @property
    def rejection_weight(self):
        return self.rejected_quantity * self.weight_per_piece

    @property
    def overall_production(self):
        return self.total_weight + self.total_scrap + self.rejection_weight
    
    # door calculations
    @property
    def door_volume(self):
        if self.height and self.width and self.thickness:
            h = self.height.height * 0.0254
            w = self.width.width * 0.0254
            t = self.thickness.thickness / 1000
            return h * w * t
        return 0

    @property
    def density_production(self):
        vol = self.door_volume
        return self.weight_per_piece / vol if vol else 0

    @property
    def door_std_weight(self):
        if self.density:
            return self.density.density * self.door_volume
        return 0

    @property
    def door_total_norm(self):
        return self.quantity * self.door_std_weight

    @property
    def door_excess(self):
        return self.total_weight - self.door_total_norm


# ================= PLANNING =================
class Planning(models.Model):
    REMARK_CHOICES = (
        ("Order", "Order"),
        ("Urgent", "Urgent"),
        ("Stock", "Stock"),
        ("J.P", "J.P"),
        ("G.P", "G.P")
    )
    
    STAMP_CHOICES = (
        ("Star", "Star"),
        ("Royal", "Royal"),
        ("Gold", "Gold"),
        ("Diamonds", "Diamonds"),
        ("Platinum", "Platinum"),
        ("Premium", "Premium")
    )
    
    MASKING_CHOICES = (
        ("Maica Masking", "Maica Masking"),
        ("Plain Masking", "Plain Masking"),
        ("Without Masking", "Without Masking")
    )

    date = models.DateField(default=timezone.now)
    category = models.CharField(max_length=10, choices=Product.CATEGORY_CHOICES)

    machine = models.ForeignKey(Machine, null=True, blank=True, on_delete=models.SET_NULL)

    thickness = models.ForeignKey(Thickness, null=True, blank=True, on_delete=models.PROTECT)
    height = models.ForeignKey(Height, null=True, blank=True, on_delete=models.PROTECT)
    width = models.ForeignKey(Width, null=True, blank=True, on_delete=models.PROTECT)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.PROTECT)
    length = models.ForeignKey(Length, null=True, blank=True, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.PROTECT)
    density = models.ForeignKey(Density, null=True, blank=True, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    weight = models.FloatField(default=0)
    stamp = models.CharField(max_length=20, choices=STAMP_CHOICES, blank=True, default="")
    masking = models.CharField(max_length=20, choices=MASKING_CHOICES, blank=True, default="")
    remark = models.CharField(max_length=20, choices=REMARK_CHOICES, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-id']

    def __str__(self):
        return f"{self.date} - {self.category} - {self.machine} - {self.quantity}"


# ================= STOCK OF PRODUCT PRODUCED =================
class Stock(models.Model):
    MOVEMENT_TYPE = (
        ('IN', 'Production'),
        ('OUT', 'Dispatch'),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    delivery_challan = models.ForeignKey(
        'DeliveryChallan',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='items'
    )

    quantity = models.FloatField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE)

    production = models.ForeignKey(Production, null=True, blank=True, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)


class DeliveryChallan(models.Model):
    challan_no = models.CharField(max_length=30, unique=True, blank=True)
    challan_date = models.DateField(default=timezone.now)
    vehicle_no = models.CharField(max_length=40)
    lr_rr_no = models.CharField(max_length=80, blank=True)
    party_name = models.CharField(max_length=200)
    party_address = models.CharField(max_length=500, blank=True)
    party_gst = models.CharField(max_length=50, blank=True)
    party_state = models.CharField(max_length=100, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=18)  # Rate per kg
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)  # GST percentage
    requirement = models.TextField(blank=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-challan_date', '-id']

    @staticmethod
    def financial_year_for(challan_date):
        start_year = challan_date.year if challan_date.month >= 4 else challan_date.year - 1
        return f"{start_year % 100:02d}-{(start_year + 1) % 100:02d}"

    def save(self, *args, **kwargs):
        if not self.challan_no:
            fy = self.financial_year_for(self.challan_date)
            prefix = f"MP/DC/{fy}/"
            last = DeliveryChallan.objects.filter(challan_no__startswith=prefix).order_by("-challan_no").first()
            next_no = 1
            if last and last.challan_no:
                try:
                    next_no = int(last.challan_no.rsplit("/", 1)[-1]) + 1
                except ValueError:
                    next_no = 1
            self.challan_no = f"{prefix}{next_no:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.challan_no


class Dispatch(models.Model):
    challan_no = models.CharField(max_length=30, unique=True)
    c_name = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='dispatches')
    lr_rr_no = models.CharField(max_length=80, blank=True)
    vehicle_no = models.CharField(max_length=40)
    remark = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.challan_no} - {self.c_name}"


# ================= RAW MATERIAL MODELS =================

class RawMaterial(models.Model):
    CATEGORY_CHOICES = (
        ('Raw Material', 'Raw Material'),
        ('Processing Head (Processing Aids)', 'Processing Head (Processing Aids)'),
        ('Stabilizer', 'Stabilizer'),
        ('CPE', 'CPE'),
        ('Lubrication', 'Lubrication'),
        ('Wax', 'Wax'),
        ('PE Wax', 'PE Wax'),
        ('Foaming White', 'Foaming White'),
        ('Foaming Yellow', 'Foaming Yellow'),
        ('Blister', 'Blister'),
        ('Scrap', 'Scrap'),
        ('Pigment', 'Pigment'),
        ('CS', 'CS'),
        ('Stearic Acid', 'Stearic Acid'),
        ('Marble Powder', 'Marble Powder'),
        ('PVC Resin', 'PVC Resin'),
        ('Internal Lubricant', 'Internal Lubricant'),
        ('External Lubricant', 'External Lubricant'),
        ('Other', 'Other'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    current_stock = models.FloatField(default=0)
    one_day_requirement = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
    



class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name



class PurchaseInvoice(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT
    )

    invoice_no = models.CharField(max_length=100)

    invoice_date = models.DateField()

    receiving_date = models.DateField()

    remarks = models.TextField(blank=True, null=True)
    
    masking = models.BooleanField(default=False)
    
    stamp = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('supplier', 'invoice_no')

    def __str__(self):
        return f"{self.supplier} - {self.invoice_no}"
    



class RawMaterialStock(models.Model):
    MOVEMENT_TYPE = (
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    )

    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    quantity = models.FloatField()
    
    rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transportation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE)

    formulation = models.ForeignKey('Formulation', null=True, blank=True, on_delete=models.PROTECT)

    batch_history = models.ForeignKey('BatchAddHistory', null=True, blank=True, on_delete=models.PROTECT, related_name='stock_deductions')

    purchase_invoice = models.ForeignKey(PurchaseInvoice,null=True,blank=True,on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)


# ================= CONSUMPTION MODELS =================

class Formulation(models.Model):
    SHIFT_CHOICES = (
        ('Day', 'Day'),
        ('Night', 'Night'),
    )

    group_name = models.CharField(max_length=100, null=True, blank=True)

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    )

    added_via_button = models.BooleanField(default=False, help_text="True if added via +Add button in UI")

    name = models.CharField(max_length=100)

    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, blank=True, default='Day')

    machine = models.ForeignKey(Machine, null=True,blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    batches = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    approved_at = models.DateTimeField(null=True, blank=True)

    is_loss = models.BooleanField(default=False)

    stock_deducted = models.BooleanField(default=False)

    planning = models.ForeignKey(Planning, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Hidden connection to Production (internal only, not visible to website users)
    production = models.ForeignKey('Production', null=True, blank=True, on_delete=models.SET_NULL, editable=False)

    def __str__(self):
        return f"{self.name} - {self.machine} - {self.shift}"
    

class FormulationItem(models.Model):
    formulation = models.ForeignKey(Formulation, on_delete=models.CASCADE, related_name='items')

    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    weight = models.FloatField()  # per batch

    def __str__(self):
        return f"{self.raw_material} - {self.weight}kg"


class BatchAddHistory(models.Model):
    """Tracks each batch addition made via the +Add button on the Formulation dashboard"""
    SHIFT_CHOICES = (
        ('Day', 'Day'),
        ('Night', 'Night'),
    )

    formulation = models.ForeignKey(Formulation, on_delete=models.CASCADE, related_name='batch_history')
    group_name = models.CharField(max_length=100)
    batch_count = models.IntegerField(default=0)
    date = models.DateField(null=True, blank=True)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, blank=True, default='Day')
    machine = models.ForeignKey(Machine, null=True, blank=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.group_name} - {self.batch_count} batches ({self.created_at:%Y-%m-%d %H:%M})"


class FormulationBatch(models.Model):
    """Saves each raw material row every time a formulation batch is added via the +Add button"""
    SHIFT_CHOICES = (
        ('Day', 'Day'),
        ('Night', 'Night'),
    )

    batch_history = models.ForeignKey(BatchAddHistory, on_delete=models.CASCADE, related_name='batches')
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    weight = models.FloatField()  # material weight per batch
    date = models.DateField(null=True, blank=True)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, blank=True, default='Day')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch_history} - {self.raw_material} - {self.weight}kg"
    

class WeightSheet(models.Model):
    SHIFT_CHOICES = (
        ('Day', 'Day'),
        ('Night', 'Night'),
    )

    CATEGORY_CHOICES = (
        ('Door', 'Door'),
        ('Frame', 'Frame'),
    )

    date = models.DateField()
    machine = models.ForeignKey('Machine', on_delete=models.PROTECT)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.machine} - {self.operator}"


    @property
    def total_rows(self):
        return self.rows.count()

    @property
    def total_weight(self):
        return sum(r.weight_per_piece for r in self.rows.all())

    @property
    def total_standard_weight(self):
        return sum(r.standard_weight for r in self.rows.all())

    @property
    def total_excess(self):
        return self.total_weight - self.total_standard_weight

    @property
    def total_excess_percent(self):
        std = self.total_standard_weight
        return (self.total_excess / std * 100) if std else 0
    

class WeightSheetRow(models.Model):
    sheet = models.ForeignKey(WeightSheet,related_name="rows",on_delete=models.PROTECT)

    thickness = models.ForeignKey('Thickness',null=True,blank=True, on_delete=models.PROTECT)
    density = models.ForeignKey('Density',null=True,blank=True, on_delete=models.PROTECT)
    color = models.ForeignKey('Color', on_delete=models.PROTECT)
    height = models.ForeignKey('Height',null=True,blank=True, on_delete=models.PROTECT)
    width = models.ForeignKey('Width',null=True,blank=True, on_delete=models.PROTECT)
    size = models.ForeignKey('Size',null=True,blank=True,on_delete=models.PROTECT)
    length = models.ForeignKey('Length',null=True,blank=True,on_delete=models.PROTECT)

    weight_per_piece = models.FloatField()

    def __str__(self):
        return f"{self.sheet} - Row {self.id}"

    @property
    def standard_weight(self):
        # DOOR
        if self.sheet.category == "Door":
            if self.height and self.width and self.thickness and self.density:
                h = self.height.height * 0.0254
                w = self.width.width * 0.0254
                t = self.thickness.thickness / 1000
                vol = h * w * t
                return round(vol * self.density.density, 3)

        # FRAME
        if self.sheet.category == "Frame":
            if self.size and self.length:
                return round(self.size.standard_weight * self.length.length,3)
        return 0

   
    @property
    def excess(self):
        return self.weight_per_piece - self.standard_weight


# ================= PERMISSIONS =================
class RolePermission(models.Model):
    """Store role-based permissions for different modules"""
    
    ROLES = (
        ('Admin', 'Admin'),
        ('Operator', 'Operator'),
        ('operator_manager', 'operator_manager'),
        ('Operator_incharge', 'Operator_incharge'),
        ('Manager', 'Manager'),
        ('Dispatch', 'Dispatch'),
        ('Batcher', 'Batcher'),
        ('Dispatch Manager', 'Dispatch Manager'),
    )
    
    MODULES = (
        ('home', 'Home'),
        ('dashboard', 'Dashboard'),
        ('planning', 'Planning'),
        ('production', 'Production'),
        ('formulation', 'Formulation'),
        ('batch', 'Batch'),
        ('master', 'Master'),
        ('stock', 'Stock'),
        ('reports', 'Reports'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES)
    module = models.CharField(max_length=50, choices=MODULES)
    has_permission = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('role', 'module')
    
    def __str__(self):
        return f"{self.role} - {self.module}: {self.has_permission}"
    
    @classmethod
    def get_role_permissions(cls, role):
        """Get all permissions for a role as a dictionary"""
        perms = cls.objects.filter(role=role).values('module', 'has_permission')
        return {perm['module']: perm['has_permission'] for perm in perms}
    
    @classmethod
    def has_module_access(cls, role, module):
        """Check if a role has access to a specific module"""
        try:
            perm = cls.objects.get(role=role, module=module)
            return perm.has_permission
        except cls.DoesNotExist:
            return False


    @classmethod
    def initialize_permissions(cls):
        """Initialize default permissions based on original logic"""
        default_perms = {
            'Admin': ['home', 'dashboard', 'planning', 'production', 'formulation', 'batch', 'master', 'stock', 'reports'],
            'Manager': ['home', 'dashboard', 'planning', 'production', 'formulation', 'batch', 'master', 'stock', 'reports'],
            'Operator': ['home', 'production', 'reports'],
            'operator_manager': ['home', 'dashboard', 'planning', 'production', 'formulation', 'batch', 'master', 'stock', 'reports'],
            'Operator_incharge': ['home', 'dashboard', 'planning', 'production', 'formulation', 'batch', 'master', 'stock', 'reports'],
            'Batcher': ['home', 'batch', 'reports'],
            'Dispatch': ['home', 'stock', 'reports'],
            'Dispatch Manager': ['home', 'stock', 'reports'],
        }
        
        all_modules = [m[0] for m in cls.MODULES]
        
        for role, role_label in cls.ROLES:
            for module in all_modules:
                cls.objects.get_or_create(
                    role=role,
                    module=module,
                    defaults={'has_permission': module in default_perms.get(role, [])}
                )

class UnfinishedProduction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    production = models.ForeignKey(Production, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.FloatField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.quantity}"


class ScrapLog(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='scrap_logs')
    quantity = models.FloatField()
    weight = models.FloatField(default=0)  # quantity * weight_per_piece
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scrap - {self.production.id} - {self.quantity}"


# ================= GROUP ORDER FOR REARRANGING =================
class GroupOrder(models.Model):
    """Store custom group display order for Production 2.0 pages"""
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='group_orders')
    category = models.CharField(max_length=10)  # 'Door' or 'Frame'
    group_key = models.CharField(max_length=500)  # unique identifier string for the group
    position = models.IntegerField()  # display order (0-based)
    
    class Meta:
        ordering = ['position']
        unique_together = ('machine', 'category', 'group_key')
    
    def __str__(self):
        return f"{self.machine.name} - {self.category} - pos {self.position}"


# ================= POWER BI DASHBOARD =================
class Dashboard(models.Model):
    """Saved Power BI dashboard configuration"""
    FORMAT_CHOICES = (
        ('chart', 'Chart View'),
        ('table', 'Table View'),
        ('pivot', 'Pivot View'),
        ('card', 'Card View'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboards')
    default_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='chart')
    layout_config = models.JSONField(default=dict, blank=True)
    filters_config = models.JSONField(default=dict, blank=True)
    pivot_config = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    auto_refresh_interval = models.IntegerField(default=0, help_text="Auto-refresh interval in seconds. 0 = manual")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"
